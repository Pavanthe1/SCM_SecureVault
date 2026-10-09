# SecureVault — ISWE305P Software Testing Project

A Flask-based cybersecurity teaching application with user accounts, AES-256-GCM, an ECC/ECDH-based authenticated-encryption workflow, a hybrid AES–ECC workflow, server-side encrypted-file storage, recovery, activity history, and automated tests.

## What changed in this final build

- Added an **Encrypted Files** page in the sidebar. Signed-in users can browse encrypted files saved in their account, download `.svlt` containers, and decrypt a saved container directly from that page by entering its encryption password.
- Encrypted and decrypted outputs are stored separately under `encrypted_files/<user_id>/` and `decrypted_files/<user_id>/` on the application server. The database, these directories, and the same deployed application must persist for cross-device access to work.
- File encryption stores the original filename in authenticated container metadata. Decryption restores that filename and extension so a recovered `.jpg` is a real JPEG, a `.pdf` is a real PDF, etc.
- The results page reports each file's success/failure, algorithm and output filename. Users can download the recovered file and open it with the appropriate desktop application.
- Prevents accidental re-encryption of `.svlt` containers (and therefore avoids `.svlt.svlt` naming errors).
- Multiple files can be selected for batch encryption/decryption.
- Login uses a non-permanent browser session and includes logout. Browser settings that restore session cookies can affect how browser restart behaves; use Logout to end the session reliably.

## Run on Windows

Install Python 3.11+ (Python 3.14 should work with current dependency wheels), then open CMD in the folder containing `app.py` and `requirements.txt`:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Keep the terminal open while running the site. Use `Ctrl+C` to stop it.

## Cross-device access after deployment

Cross-device access means the browser on device A uploads the file to the same deployed SecureVault server, and a later login from device B retrieves it from that server-side account vault. It does **not** mean files sync between separate local copies of the project.

Before deployment, configure:

- `SECUREVAULT_SECRET`: a long random secret that remains unchanged across restarts and instances.
- `SECUREVAULT_DB`: path to a persistent SQLite database (or adapt the project to a managed database for multi-instance production use).
- `SECUREVAULT_ENCRYPTED_DIR` and `SECUREVAULT_DECRYPTED_DIR`: persistent private storage directories/volumes. Do not use an ephemeral filesystem if files must survive redeploys.
- `HOST=0.0.0.0` and the hosting provider's `PORT` as needed.
- `SECURE_COOKIE=1` when served over HTTPS.

A single-instance host with a persistent disk is appropriate for this course demonstration. If the host deletes local storage on redeploy, saved files will be lost. Never commit real user files, passwords, secrets, database files, or encryption keys to source control. The application is an educational prototype and has not been security-audited for sensitive production use.

## Cryptography summary

- **AES-256-GCM:** password-derived key using Scrypt, authenticated encryption.
- **ECC-ECDH-GCM:** elliptic-curve Diffie–Hellman derives the AES-GCM data key; it is an ECC-based key-agreement construction, not direct large-file ECC encryption.
- **Hybrid AES–ECC:** a random AES-256 key encrypts the file; an ECDH-derived AES-GCM key protects the data key.
- All modes store a SHA-256 digest and check it after authenticated decryption.

Encrypted `.svlt` files are supposed to be unreadable as images/documents. Decryption produces a separate original-format file. On Windows, download the recovered image and open it with Photos (or double-click it if Photos is the default application). A web browser cannot reliably force Windows to launch a specific desktop app.

## Tests and course evidence

Run unit and web tests:

```bat
python -m pytest -q
```

Performance test script: `performance_locust.py` (requires Locust; install with `pip install locust`, then run `locust -f performance_locust.py`). Capture the Locust Statistics and Charts pages during your own run. Record actual output, failures, response times and environment in the RTM/test matrix; do not use example benchmark data as actual results.

The project includes a test report/SRS and screenshot checklist in `docs/`. Review and update those documents with screenshots and measured outcomes from the final build before submitting. JUnit is a Java testing framework and cannot directly execute Python Flask functions; if your instructor requires literal JUnit, provide a small genuine Java/JUnit component/test adapter and document its boundary rather than labelling pytest results as JUnit.
