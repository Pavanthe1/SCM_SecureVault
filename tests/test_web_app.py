import io
import app as webapp
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(webapp, 'DB', tmp_path/'test.db')
    monkeypatch.setattr(webapp, 'ENCRYPTED_ROOT', tmp_path/'encrypted_files')
    monkeypatch.setattr(webapp, 'DECRYPTED_ROOT', tmp_path/'decrypted_files')
    with webapp.app.app_context():
        webapp.db().execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        webapp.db().execute('''CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, action TEXT NOT NULL, algorithm TEXT NOT NULL, filename TEXT NOT NULL, file_size INTEGER NOT NULL, elapsed REAL NOT NULL, status TEXT NOT NULL, sha256 TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        webapp.db().commit()
    webapp.app.config.update(TESTING=True, SECRET_KEY='test-secret')
    with webapp.app.test_client() as c:
        yield c

def register(client):
    return client.post('/register', data={'username':'tester_01','password':'Strong-password-123'}, follow_redirects=True)

def test_dashboard_requires_login(client):
    r=client.get('/dashboard'); assert r.status_code==302 and '/login' in r.location

def test_register_and_dashboard(client):
    r=register(client); assert r.status_code==200 and b'Choose your strategy' in r.data

def test_login_rejects_wrong_password(client):
    register(client); client.post('/logout'); r=client.post('/login',data={'username':'tester_01','password':'wrong'},follow_redirects=True); assert b'incorrect' in r.data

def test_encrypt_saves_file_and_result_has_success(client):
    register(client)
    r=client.post('/encrypt/hybrid',data={'files':(io.BytesIO(b'web flow content'),'sample.txt'),'password':'My-Strong-Passphrase-123','confirm':'My-Strong-Passphrase-123'},content_type='multipart/form-data')
    assert r.status_code==200 and b'Encryption completed' in r.data and b'sample.txt.svlt' in r.data
    listing=client.get('/files')
    assert listing.status_code==200 and b'sample.txt.svlt' in listing.data and b'Decrypt' in listing.data

def test_decrypt_saved_file_from_vault_preserves_original_filename(client):
    register(client)
    client.post('/encrypt/hybrid',data={'files':(io.BytesIO(b'image-like-content'),'photo.jpg'),'password':'My-Strong-Passphrase-123','confirm':'My-Strong-Passphrase-123'},content_type='multipart/form-data')
    r=client.post('/vault/decrypt/photo.jpg.svlt',data={'password':'My-Strong-Passphrase-123'})
    assert r.status_code==200 and b'Decryption completed' in r.data and b'photo.jpg' in r.data
    download=client.get('/output/decrypted/photo.jpg')
    assert download.status_code==200 and download.data==b'image-like-content'

def test_wrong_password_does_not_create_decrypted_output(client):
    register(client)
    client.post('/encrypt/aes',data={'files':(io.BytesIO(b'secret'),'note.txt'),'password':'My-Strong-Passphrase-123','confirm':'My-Strong-Passphrase-123'},content_type='multipart/form-data')
    r=client.post('/vault/decrypt/note.txt.svlt',data={'password':'wrong-password'},follow_redirects=True)
    assert r.status_code==200 and b'Decryption failed' in r.data
    assert client.get('/output/decrypted/note.txt').status_code==302

def test_reject_reencrypting_svlt(client):
    register(client)
    r=client.post('/encrypt/aes',data={'files':(io.BytesIO(b'container'),'already.svlt'),'password':'My-Strong-Passphrase-123','confirm':'My-Strong-Passphrase-123'},content_type='multipart/form-data')
    assert r.status_code==200 and b'already a SecureVault encrypted file' in r.data

def test_password_confirmation_mismatch(client):
    register(client); r=client.post('/encrypt/aes',data={'file':(io.BytesIO(b'x'),'x.txt'),'password':'Strong-password-123','confirm':'different'},content_type='multipart/form-data',follow_redirects=True); assert b'does not match' in r.data

def test_unknown_encryption_mode_redirects(client):
    register(client); r=client.get('/encrypt/not-a-mode'); assert r.status_code==302
