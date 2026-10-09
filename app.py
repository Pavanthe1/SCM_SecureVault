import os, sqlite3, time
from functools import wraps
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from crypto_engine import encrypt, decrypt

BASE = Path(__file__).resolve().parent
DB = Path(os.environ.get('SECUREVAULT_DB', str(BASE / 'securevault.db')))
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECUREVAULT_SECRET', 'dev-only-change-this-secret-before-deployment'),
    MAX_CONTENT_LENGTH=500 * 1024 * 1024,
    SESSION_PERMANENT=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('SECURE_COOKIE', '0') == '1',
)
ENCRYPTED_ROOT = Path(os.environ.get('SECUREVAULT_ENCRYPTED_DIR', str(BASE / 'encrypted_files')))
DECRYPTED_ROOT = Path(os.environ.get('SECUREVAULT_DECRYPTED_DIR', str(BASE / 'decrypted_files')))
ENCRYPTED_ROOT.mkdir(parents=True, exist_ok=True)
DECRYPTED_ROOT.mkdir(parents=True, exist_ok=True)
ALGORITHMS = {'aes': 'AES-256-GCM', 'ecc': 'ECC-ECDH-GCM', 'hybrid': 'HYBRID-AES-ECC'}


def db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db


@app.teardown_appcontext
def close_db(exc):
    conn = g.pop('db', None)
    if conn is not None:
        conn.close()


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as c:
        c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        c.execute('''CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, action TEXT NOT NULL,
            algorithm TEXT NOT NULL, filename TEXT NOT NULL, file_size INTEGER NOT NULL,
            elapsed REAL NOT NULL, status TEXT NOT NULL, sha256 TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))''')


init_db()


@app.before_request
def non_persistent_login():
    # Browser-session cookie: users must sign in again after the browser session ends.
    session.permanent = False


def user_storage(root):
    folder = root / str(session['user_id'])
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapped


def log(action, algo, filename, size, elapsed, status, digest=None):
    db().execute('INSERT INTO history(user_id,action,algorithm,filename,file_size,elapsed,status,sha256) VALUES(?,?,?,?,?,?,?,?)',
                 (session['user_id'], action, algo, filename, size, elapsed, status, digest))
    db().commit()


def safe_original_name(name, fallback='recovered-file'):
    name = secure_filename(name or '')
    return name or fallback


def unique_path(folder, filename):
    candidate = folder / filename
    if not candidate.exists():
        return candidate
    path = Path(filename)
    stamp = time.strftime('%Y%m%d_%H%M%S')
    candidate = folder / f'{path.stem}_{stamp}{path.suffix}'
    counter = 2
    while candidate.exists():
        candidate = folder / f'{path.stem}_{stamp}_{counter}{path.suffix}'
        counter += 1
    return candidate


def stored_files(root):
    folder = user_storage(root)
    entries = []
    for p in sorted(folder.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.is_file() and not p.name.startswith('.'):
            stat = p.stat()
            entries.append({'name': p.name, 'size': stat.st_size, 'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))})
    return entries


@app.context_processor
def common():
    return {'active_user': session.get('username'), 'year': time.localtime().tm_year}


@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if len(username) < 3 or len(username) > 40 or not username.replace('_', '').replace('-', '').isalnum():
            flash('Use 3–40 letters, numbers, underscores or hyphens for your username.', 'error')
        elif len(password) < 10:
            flash('Use a password with at least 10 characters.', 'error')
        else:
            try:
                cur = db().execute('INSERT INTO users(username,password_hash) VALUES(?,?)', (username, generate_password_hash(password)))
                db().commit()
                session.clear(); session['user_id'] = cur.lastrowid; session['username'] = username
                flash('Your secure workspace is ready.', 'success')
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                flash('That username already exists. Choose another.', 'error')
    return render_template('auth.html', mode='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        row = db().execute('SELECT * FROM users WHERE username=?', (request.form.get('username', '').strip(),)).fetchone()
        if row and check_password_hash(row['password_hash'], request.form.get('password', '')):
            session.clear(); session['user_id'] = row['id']; session['username'] = row['username']
            return redirect(url_for('dashboard'))
        flash('Username or password is incorrect.', 'error')
    return render_template('auth.html', mode='login')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been signed out.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    rows = db().execute('SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 6', (session['user_id'],)).fetchall()
    stats = db().execute("SELECT COUNT(*) total, SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) passed, SUM(file_size) bytes FROM history WHERE user_id=?", (session['user_id'],)).fetchone()
    return render_template('dashboard.html', recent=rows, stats=stats)


@app.route('/encrypt/<mode>', methods=['GET', 'POST'])
@login_required
def encrypt_page(mode):
    if mode not in ALGORITHMS:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        uploads = [f for f in request.files.getlist('files') if f and f.filename]
        if not uploads:
            single = request.files.get('file')
            if single and single.filename:
                uploads = [single]
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        if not uploads:
            flash('Choose at least one file before starting encryption.', 'error')
        elif not password:
            flash('Enter a password to protect the encryption key.', 'error')
        elif password != confirm:
            flash('The password confirmation does not match.', 'error')
        else:
            results = []
            outdir = user_storage(ENCRYPTED_ROOT)
            for f in uploads:
                filename = safe_original_name(f.filename, 'uploaded-file')
                start = time.perf_counter()
                try:
                    if filename.lower().endswith('.svlt'):
                        raise ValueError('This is already a SecureVault encrypted file. Use Encrypted Files or Decrypt a file instead of encrypting it again.')
                    data = f.read()
                    encrypted, meta = encrypt(data, password, ALGORITHMS[mode], original_filename=filename)
                    elapsed = time.perf_counter() - start
                    dest = unique_path(outdir, filename + '.svlt')
                    dest.write_bytes(encrypted)
                    log('ENCRYPT', ALGORITHMS[mode], filename, len(data), elapsed, 'SUCCESS', meta.get('original_sha256'))
                    results.append({'name': filename, 'output': dest.name, 'kind': 'encrypted', 'size': len(encrypted), 'algorithm': ALGORITHMS[mode], 'status': 'SUCCESS'})
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    log('ENCRYPT', ALGORITHMS[mode], filename, 0, elapsed, 'FAILED')
                    results.append({'name': filename, 'output': '', 'kind': 'encrypted', 'size': 0, 'algorithm': ALGORITHMS[mode], 'status': 'FAILED', 'error': str(e)})
            return render_template('results.html', action='Encryption', results=results, folder='encrypted_files')
    return render_template('encrypt.html', mode=mode, algorithm=ALGORITHMS[mode])


def decrypt_and_store(blob, uploaded_name, password):
    plain, result = decrypt(blob, password)
    original = safe_original_name(result.get('original_filename'), '')
    if not original:
        # Compatibility with older SecureVault containers without original_filename metadata.
        original = safe_original_name(uploaded_name[:-5] if uploaded_name.lower().endswith('.svlt') else uploaded_name, 'recovered-file')
    outdir = user_storage(DECRYPTED_ROOT)
    dest = unique_path(outdir, original)
    dest.write_bytes(plain)
    return dest, plain, result


@app.route('/decrypt', methods=['GET', 'POST'])
@login_required
def decrypt_page():
    if request.method == 'POST':
        uploads = [f for f in request.files.getlist('files') if f and f.filename]
        if not uploads:
            single = request.files.get('file')
            if single and single.filename:
                uploads = [single]
        password = request.form.get('password', '')
        if not uploads:
            flash('Choose at least one SecureVault .svlt file to decrypt.', 'error')
        elif not password:
            flash('Enter the password used during encryption.', 'error')
        else:
            results = []
            for f in uploads:
                filename = safe_original_name(f.filename, 'encrypted-file.svlt')
                start = time.perf_counter(); blob = f.read()
                try:
                    dest, plain, result = decrypt_and_store(blob, filename, password)
                    elapsed = time.perf_counter() - start
                    log('DECRYPT', result['algorithm'], dest.name, len(plain), elapsed, 'SUCCESS', result['sha256'])
                    results.append({'name': filename, 'output': dest.name, 'kind': 'decrypted', 'size': len(plain), 'algorithm': result['algorithm'], 'status': 'SUCCESS', 'sha256': result['sha256']})
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    log('DECRYPT', 'AUTO-DETECT', filename, len(blob), elapsed, 'FAILED')
                    results.append({'name': filename, 'output': '', 'kind': 'decrypted', 'size': len(blob), 'algorithm': 'AUTO-DETECT', 'status': 'FAILED', 'error': str(e)})
            return render_template('results.html', action='Decryption', results=results, folder='decrypted_files')
    return render_template('decrypt.html')


@app.route('/vault/decrypt/<path:filename>', methods=['POST'])
@login_required
def decrypt_saved_file(filename):
    safe = secure_filename(filename)
    source = user_storage(ENCRYPTED_ROOT) / safe
    password = request.form.get('password', '')
    if not source.is_file():
        flash('Encrypted file not found in your vault.', 'error')
        return redirect(url_for('files_page'))
    if not password:
        flash('Enter the encryption password first.', 'error')
        return redirect(url_for('files_page'))
    blob = source.read_bytes(); start = time.perf_counter()
    try:
        dest, plain, result = decrypt_and_store(blob, safe, password)
        elapsed = time.perf_counter() - start
        log('DECRYPT', result['algorithm'], dest.name, len(plain), elapsed, 'SUCCESS', result['sha256'])
        return render_template('results.html', action='Decryption', folder='decrypted_files', results=[{'name': safe, 'output': dest.name, 'kind': 'decrypted', 'size': len(plain), 'algorithm': result['algorithm'], 'status': 'SUCCESS', 'sha256': result['sha256']}])
    except Exception as e:
        elapsed = time.perf_counter() - start
        log('DECRYPT', 'AUTO-DETECT', safe, len(blob), elapsed, 'FAILED')
        flash(f'Decryption failed: {e}', 'error')
        return redirect(url_for('files_page'))


@app.route('/output/<kind>/<path:filename>')
@login_required
def download_output(kind, filename):
    if kind not in ('encrypted', 'decrypted'):
        return redirect(url_for('dashboard'))
    root = ENCRYPTED_ROOT if kind == 'encrypted' else DECRYPTED_ROOT
    safe = secure_filename(filename)
    path = user_storage(root) / safe
    if not path.is_file():
        flash('That output file was not found in your workspace.', 'error')
        return redirect(url_for('files_page'))
    return send_file(path, as_attachment=True, download_name=safe, conditional=True)


@app.route('/files')
@login_required
def files_page():
    encrypted = stored_files(ENCRYPTED_ROOT)
    decrypted = stored_files(DECRYPTED_ROOT)
    rows = db().execute('SELECT * FROM history WHERE user_id=? ORDER BY id DESC LIMIT 100', (session['user_id'],)).fetchall()
    return render_template('files.html', encrypted=encrypted, decrypted=decrypted, rows=rows)


@app.route('/history')
@login_required
def history_page():
    rows = db().execute('SELECT * FROM history WHERE user_id=? ORDER BY id DESC', (session['user_id'],)).fetchall()
    return render_template('history.html', rows=rows)


@app.route('/keys')
@login_required
def keys_page():
    return render_template('keys.html')


@app.errorhandler(413)
def too_large(e):
    flash('Upload exceeds the 500 MB request limit. Try fewer or smaller files.', 'error')
    return redirect(request.referrer or url_for('dashboard'))


if __name__ == '__main__':
    # Bind locally by default. Deployment hosts can set HOST=0.0.0.0 and PORT.
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1', host=os.environ.get('HOST', '127.0.0.1'), port=int(os.environ.get('PORT', '5000')))
