import pytest
from crypto_engine import encrypt, decrypt, unpack

ALGORITHMS = ['AES-256-GCM', 'ECC-ECDH-GCM', 'HYBRID-AES-ECC']
PAYLOADS = [b'Hello SecureVault', b'', bytes(range(256))*16, b'\x00\xff\x10binary\nfile']

@pytest.mark.parametrize('algorithm', ALGORITHMS)
@pytest.mark.parametrize('payload', PAYLOADS)
def test_round_trip_all_algorithms(algorithm, payload):
    encrypted, meta = encrypt(payload, 'Correct-Horse-Battery-123!', algorithm)
    recovered, result = decrypt(encrypted, 'Correct-Horse-Battery-123!')
    assert recovered == payload
    assert result['integrity'] == 'VERIFIED'
    assert result['sha256'] == meta['original_sha256']
    assert result['algorithm'] == algorithm

def test_wrong_password_rejected_aes():
    encrypted, _ = encrypt(b'secret', 'correct password', 'AES-256-GCM')
    with pytest.raises(ValueError, match='Authentication failed'):
        decrypt(encrypted, 'wrong password')

@pytest.mark.parametrize('algorithm', ALGORITHMS)
def test_wrong_password_rejected_all_modes(algorithm):
    encrypted, _ = encrypt(b'secret', 'correct password', algorithm)
    with pytest.raises(ValueError): decrypt(encrypted, 'wrong password')

def test_corrupted_ciphertext_rejected():
    encrypted, _ = encrypt(b'this must remain authentic', 'password-12345', 'HYBRID-AES-ECC')
    damaged = bytearray(encrypted); damaged[-1] ^= 1
    with pytest.raises(ValueError): decrypt(bytes(damaged), 'password-12345')

def test_invalid_header_rejected():
    with pytest.raises(ValueError, match='not a SecureVault'):
        decrypt(b'not encrypted data', 'password')

def test_truncated_metadata_rejected():
    encrypted, _ = encrypt(b'content', 'password-12345', 'AES-256-GCM')
    with pytest.raises(ValueError): decrypt(encrypted[:14], 'password-12345')

def test_metadata_algorithm_mismatch_rejected():
    encrypted, _ = encrypt(b'content', 'password-12345', 'AES-256-GCM')
    meta, cipher = unpack(encrypted); meta['algorithm'] = 'HYBRID-AES-ECC'
    # Repack through the module's defined container format to ensure a syntactically valid but incompatible file.
    import json, struct
    from crypto_engine import MAGIC, b64
    meta['ciphertext'] = b64(cipher); raw = json.dumps(meta,separators=(',',':')).encode()
    forged = MAGIC + struct.pack('>I',len(raw)) + raw
    with pytest.raises(ValueError): decrypt(forged, 'password-12345')

def test_missing_password_rejected():
    with pytest.raises(ValueError, match='password'):
        encrypt(b'content', '', 'AES-256-GCM')
