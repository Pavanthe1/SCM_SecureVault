"""Authenticated file encryption strategies for SecureVault.

ECC mode: ECDH-derived AES-256-GCM data key (ECIES-style envelope).
Hybrid mode: random AES-256-GCM data key, wrapped by an ECDH-derived AES-GCM key.
Private keys are encrypted at rest inside the encrypted-file container using a
password-derived key. This is a teaching/demo application, not a certified product.
"""
import base64, hashlib, json, os, struct
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

MAGIC = b'SVLT1\n'
VERSION = 1

def b64(b: bytes) -> str: return base64.urlsafe_b64encode(b).decode('ascii')
def unb64(s: str) -> bytes: return base64.urlsafe_b64decode(s.encode('ascii'))
def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def password_key(password: str, salt: bytes) -> bytes:
    if not password: raise ValueError('A password is required.')
    return Scrypt(salt=salt, length=32, n=2**14, r=8, p=1).derive(password.encode('utf-8'))
def hkdf(secret: bytes, salt: bytes, info: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info).derive(secret)
def public_pem(key) -> bytes:
    return key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
def private_pem(key) -> bytes:
    return key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
def load_pub(data: bytes): return serialization.load_pem_public_key(data)
def load_priv(data: bytes): return serialization.load_pem_private_key(data, password=None)
def pack(meta: dict, ciphertext: bytes) -> bytes:
    meta['ciphertext'] = b64(ciphertext)
    raw = json.dumps(meta, separators=(',', ':')).encode()
    return MAGIC + struct.pack('>I', len(raw)) + raw

def unpack(blob: bytes):
    if not blob.startswith(MAGIC) or len(blob) < len(MAGIC)+4: raise ValueError('This is not a SecureVault encrypted file or its header is damaged.')
    n = struct.unpack('>I', blob[len(MAGIC):len(MAGIC)+4])[0]
    start = len(MAGIC)+4
    if n < 2 or n > 2_000_000 or len(blob) < start+n: raise ValueError('Encrypted file metadata is damaged or incomplete.')
    try: meta = json.loads(blob[start:start+n].decode())
    except Exception as e: raise ValueError('Encrypted file metadata is invalid.') from e
    try: cipher = unb64(meta.pop('ciphertext'))
    except Exception as e: raise ValueError('Encrypted file ciphertext is missing or invalid.') from e
    return meta, cipher

def protect_private_key(priv: ec.EllipticCurvePrivateKey, password: str) -> dict:
    salt, nonce = os.urandom(16), os.urandom(12)
    key = password_key(password, salt)
    encrypted = AESGCM(key).encrypt(nonce, private_pem(priv), b'SecureVault private key v1')
    return {'key_salt': b64(salt), 'key_nonce': b64(nonce), 'private_key_box': b64(encrypted)}
def unlock_private_key(meta: dict, password: str):
    try:
        key = password_key(password, unb64(meta['key_salt']))
        pem = AESGCM(key).decrypt(unb64(meta['key_nonce']), unb64(meta['private_key_box']), b'SecureVault private key v1')
        return load_priv(pem)
    except (InvalidTag, KeyError, ValueError) as e: raise ValueError('Incorrect password or damaged encrypted key.') from e

def encrypt(data: bytes, password: str, algorithm: str, original_filename: str = ""):
    if not isinstance(data, bytes): raise TypeError('File data must be bytes.')
    if not password: raise ValueError('Enter a password before encrypting.')
    salt, nonce = os.urandom(16), os.urandom(12)
    common = {'format':'SecureVault','version':VERSION,'algorithm':algorithm,'original_filename': original_filename, 'original_sha256':sha256(data),'original_size':len(data),'salt':b64(salt),'nonce':b64(nonce)}
    if algorithm == 'AES-256-GCM':
        key = password_key(password, salt)
        ciphertext = AESGCM(key).encrypt(nonce, data, b'SecureVault AES-256-GCM v1')
        common['kdf'] = 'scrypt'
    elif algorithm in ('ECC-ECDH-GCM', 'HYBRID-AES-ECC'):
        recipient = ec.generate_private_key(ec.SECP256R1())
        ephemeral = ec.generate_private_key(ec.SECP256R1())
        shared = ephemeral.exchange(ec.ECDH(), recipient.public_key())
        common.update(protect_private_key(recipient, password))
        common['ephemeral_public_key'] = b64(public_pem(ephemeral.public_key()))
        common['curve'] = 'secp256r1'
        if algorithm == 'ECC-ECDH-GCM':
            key = hkdf(shared, salt, b'SecureVault ECC data key v1')
            ciphertext = AESGCM(key).encrypt(nonce, data, b'SecureVault ECC-ECDH-GCM v1')
        else:
            data_key = os.urandom(32)
            wrap_key = hkdf(shared, salt, b'SecureVault hybrid AES key wrapping v1')
            wrap_nonce = os.urandom(12)
            common['wrapped_key_nonce'] = b64(wrap_nonce)
            common['wrapped_aes_key'] = b64(AESGCM(wrap_key).encrypt(wrap_nonce, data_key, b'SecureVault AES key v1'))
            ciphertext = AESGCM(data_key).encrypt(nonce, data, b'SecureVault HYBRID-AES-ECC v1')
            common['key_strategy'] = 'random AES-256 key wrapped with ECDH-derived AES-GCM key'
    else: raise ValueError('Unsupported encryption strategy.')
    return pack(common, ciphertext), common

def decrypt(blob: bytes, password: str):
    meta, ciphertext = unpack(blob)
    if meta.get('format') != 'SecureVault' or meta.get('version') != VERSION: raise ValueError('Unsupported encrypted-file format.')
    algorithm = meta.get('algorithm')
    try:
        if algorithm == 'AES-256-GCM':
            key = password_key(password, unb64(meta['salt']))
            plain = AESGCM(key).decrypt(unb64(meta['nonce']), ciphertext, b'SecureVault AES-256-GCM v1')
        elif algorithm in ('ECC-ECDH-GCM', 'HYBRID-AES-ECC'):
            priv = unlock_private_key(meta, password)
            eph = load_pub(unb64(meta['ephemeral_public_key']))
            shared = priv.exchange(ec.ECDH(), eph)
            salt = unb64(meta['salt'])
            if algorithm == 'ECC-ECDH-GCM':
                key = hkdf(shared, salt, b'SecureVault ECC data key v1')
                plain = AESGCM(key).decrypt(unb64(meta['nonce']), ciphertext, b'SecureVault ECC-ECDH-GCM v1')
            else:
                wrap_key = hkdf(shared, salt, b'SecureVault hybrid AES key wrapping v1')
                data_key = AESGCM(wrap_key).decrypt(unb64(meta['wrapped_key_nonce']), unb64(meta['wrapped_aes_key']), b'SecureVault AES key v1')
                plain = AESGCM(data_key).decrypt(unb64(meta['nonce']), ciphertext, b'SecureVault HYBRID-AES-ECC v1')
        else: raise ValueError('Unknown algorithm. Choose the matching SecureVault decryption workflow.')
    except InvalidTag as e: raise ValueError('Authentication failed: wrong password, corrupted file, or incompatible decryption data.') from e
    except (KeyError, TypeError, ValueError) as e:
        if isinstance(e, ValueError) and str(e).startswith(('Authentication failed:', 'Incorrect password', 'This is not a SecureVault', 'Encrypted file', 'Unsupported', 'Unknown algorithm')): raise
        raise ValueError('Encrypted file metadata is incomplete or incompatible with the selected strategy.') from e
    actual = sha256(plain)
    if actual != meta.get('original_sha256'): raise ValueError('Integrity check failed: SHA-256 does not match the original file.')
    return plain, {'algorithm':algorithm,'sha256':actual,'integrity':'VERIFIED','size':len(plain),'original_filename':meta.get('original_filename') or ''}
