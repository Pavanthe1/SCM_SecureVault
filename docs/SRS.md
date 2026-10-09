# Software Requirements Specification (SRS)
## SecureVault — Authenticated File Encryption and Decryption

**Course:** ISWE305P Software Testing · Fall Semester 2026–2027  
**School:** School of Computer Science Engineering and Information Systems, VIT Vellore  
**Version:** 1.0 · **Date:** 9 October 2026

## 1. Introduction

### 1.1 Purpose
SecureVault is a browser-based educational cybersecurity application that demonstrates secure file encryption and recovery through three cryptographic strategies: password-derived AES-256-GCM, ECC/ECDH-derived AES-GCM, and hybrid AES–ECC key wrapping. The project provides a practical system on which black-box, unit, integration, and non-functional testing can be performed.

### 1.2 Scope
The application allows a user to register and sign in, upload a file, choose an encryption strategy, download an encrypted `.svlt` container, upload that container for decryption, and receive the recovered file only when authenticated decryption and SHA-256 verification succeed. It records operation metadata for the signed-in user. The application is a course demonstration and is not a certified production file-vault service.

### 1.3 Definitions
- **AES-GCM:** Authenticated symmetric encryption that detects ciphertext modification.
- **ECC / ECDH:** Elliptic-curve cryptography / elliptic-curve Diffie–Hellman key agreement.
- **Hybrid AES–ECC:** AES encrypts file contents; an ECDH/HKDF-derived key protects the random AES data key.
- **KDF:** Key derivation function; scrypt derives a key from a password and random salt.
- **SHA-256:** Cryptographic digest used to compare recovered data against the digest recorded during encryption.
- **RTM:** Requirements Traceability Matrix linking requirements to tests.

## 2. Overall Description

### 2.1 Product perspective
SecureVault is a Flask web application with HTML, CSS and JavaScript pages, a SQLite database for accounts and operation history, and a cryptographic service module. Files are uploaded to the local web process and encrypted/decrypted in memory. Results are streamed to the browser as downloads; original files are not stored in a server-side file archive.

### 2.2 User classes
- **Registered user:** Can access the workspace, run encryption/decryption, review their operation history and read key-management explanations.
- **Unauthenticated visitor:** Can register or sign in only; workspace pages redirect to login.
- **Project tester:** Uses valid, invalid, boundary and tampered inputs to verify functional and non-functional requirements.

### 2.3 Operating environment
Python 3.10 or later, Flask, the `cryptography` package, SQLite and a modern browser on Windows, Linux or macOS. Development is intended for localhost. The web app enforces a 100 MB request-size cap; current file processing reads uploaded content into memory and is not streaming/chunked encryption.

### 2.4 Constraints and assumptions
The user must retain the original encryption password. The `.svlt` file must not be altered. The application assumes the local server and its host are trusted. The course demo is not a replacement for audited cryptographic products, managed recipient keys, a hardware-backed key store, or production web hardening.

## 3. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The system shall allow a user to register with a unique username and password of at least 10 characters. | High |
| FR-02 | The system shall authenticate users and restrict workspace routes to signed-in users. | High |
| FR-03 | The system shall accept a file upload for encryption and reject a missing file. | High |
| FR-04 | The system shall provide AES-256-GCM encryption with a scrypt-derived key and random salt/nonce. | High |
| FR-05 | The system shall provide an ECC/ECDH-derived AES-GCM workflow distinct from standalone password-derived AES. | High |
| FR-06 | The system shall provide hybrid AES–ECC encryption using a random AES data key and ECC-derived key wrapping. | High |
| FR-07 | The system shall package strategy metadata, authentication data and the original SHA-256 digest into a `.svlt` container. | High |
| FR-08 | The system shall decrypt a supported container using its embedded strategy metadata and the correct password. | High |
| FR-09 | The system shall reject a wrong password, tampered ciphertext, damaged header, malformed metadata or incompatible strategy data. | High |
| FR-10 | The system shall verify the recovered data's SHA-256 digest before returning the recovered file. | High |
| FR-11 | The system shall return successful encryption/decryption results as browser downloads. | High |
| FR-12 | The system shall record operation, algorithm, filename, size, elapsed time, status and digest metadata per user. | Medium |
| FR-13 | The system shall display strategy explanations and key-management information. | Medium |
| FR-14 | The system shall reject uploads above the configured 100 MB limit with a user-readable message. | Medium |

## 4. Non-Functional Requirements

- **NFR-01 Security:** Use authenticated AES-GCM encryption and reject authentication failures; never store account passwords as plaintext.
- **NFR-02 Integrity:** Return plaintext only after successful authentication and digest verification.
- **NFR-03 Usability:** Main actions must be reachable from the navigation and display clear error/success feedback.
- **NFR-04 Performance:** Record encryption/decryption time for multiple file sizes and compare algorithms using repeatable runs.
- **NFR-05 Reliability:** Invalid or damaged inputs must result in controlled errors rather than unhandled application crashes.
- **NFR-06 Compatibility:** Support a current desktop browser and Python 3.10+ environment.
- **NFR-07 Auditability:** Preserve operation metadata for the authenticated user.
- **NFR-08 Maintainability:** Separate routes, cryptographic functions, templates, styles, scripts and tests.

## 5. Modules and Interface Screens

1. **User Authentication:** Register/sign-in and session-based route protection.
2. **AES Encryption/Decryption:** Password-derived AES-256-GCM file encryption.
3. **ECC Key Management / ECC workflow:** ECDH key agreement, HKDF and password-protected private-key material in the container.
4. **Hybrid AES–ECC:** Random AES data key, AES-GCM file encryption, and ECC-derived wrapping key.
5. **File Management:** Upload and download workflows plus recorded file-operation activity.
6. **Encryption History:** User-scoped event list, status, size and elapsed time.

Screens designed in the web application: authentication, overview dashboard, AES encryption, ECC encryption, hybrid encryption, decryption, key management, file activity and audit history.

## 6. Acceptance Criteria

The project is acceptable for demonstration when: (1) the user can register/sign in; (2) each of the three strategies can encrypt and recover binary/text/empty test files; (3) wrong passwords and tampered containers are rejected; (4) recovered SHA-256 matches the original; (5) encrypted and recovered downloads are returned; (6) operation history is recorded; (7) critical cryptographic tests pass; and (8) a performance tool is executed and its actual results/screenshots are attached by the student.

## 7. Known Limitations

This is an educational prototype. It does not implement streamed/chunked file encryption, CSRF protection, rate limiting, an external key vault, production-grade session hardening or a full recipient public-key distribution model. The hybrid workflow is the recommended project focus for explaining separation of data encryption and key protection. Performance figures must be reported with the machine, Python/library versions, sample sizes and iteration count; results are environment-dependent.
