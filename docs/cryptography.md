# Cryptography

This document describes the cryptographic design of roXac.

---

## Algorithms

| Purpose                  | Algorithm               |
| ------------------------ | ----------------------- |
| Password hashing         | Argon2id                |
| Master key derivation    | Argon2id                |
| Key encapsulation        | ML-KEM-768 (FIPS 203)   |
| Authenticated encryption | AES-256-GCM             |
| Randomness               | Operating system CSPRNG |

---

## Password Protection

The user's password is never stored in plaintext.

During first-time setup:
1. A random salt is generated.
2. The password is hashed using Argon2id.
3. The hash is stored in `auth.hash`.

Future logins verify the entered password against this hash.

---

## Master Key Derivation

A separate Argon2id invocation derives a deterministic 32-byte master key from the password and a stored master key salt.

The master key is never written to disk. It is regenerated from the password on each authenticated command and used only to encrypt and decrypt the ML-KEM private key.

---

## ML-KEM Key Pair

During first-time setup, roXac generates a single ML-KEM-768 key pair.

- The public key is stored unencrypted in `kem_public.key`.
- The private key is encrypted with the master key (AES-256-GCM) and stored in `kem_private.enc`.

The private key is never stored in plaintext.

---

## History Encryption

Every calculation is encrypted independently.

For each history entry:
1. The ML-KEM public key encapsulates a fresh shared secret → `(kem_ciphertext, shared_secret)`.
2. The shared secret becomes the AES-256-GCM key.
3. A random nonce is generated.
4. The entry is encrypted.
5. `kem_ciphertext + nonce + aes_ciphertext` is appended to `history.enc`.

Each entry receives a unique encryption key. Compromise of one entry does not expose any other.

---

## Reading History

```
Password
    │
    ▼
Argon2id → Master Key
    │
    ▼
Decrypt ML-KEM private key (AES-256-GCM)
    │
    ▼
Decapsulate shared secrets (ML-KEM)
    │
    ▼
Decrypt history entries (AES-256-GCM)
```

Without the correct password, the private key cannot be recovered and history cannot be decrypted.

---

## Password and History Are Decoupled

History is encrypted using independently generated ML-KEM shared secrets, not directly with the password.

This means the password only protects the private key wrapper. The history itself is unaffected by password operations. A future password change would only require re-encrypting `kem_private.enc`, not the entire history.

Password change is not implemented in v1.0.0.

---

## AES-256-GCM

Provides confidentiality, authentication, and integrity. If ciphertext is tampered with, decryption fails rather than returning corrupted plaintext.

---

## Argon2id

Used for two independent purposes:

- **Password hashing** — verifies future logins via `auth.hash`.
- **Master key derivation** — derives the key used to protect `kem_private.enc`.

These are separate invocations with separate salts. The stored password hash is never used as an encryption key.

---

## ML-KEM-768

NIST-standardised post-quantum Key Encapsulation Mechanism (FIPS 203). Used exclusively for generating per-entry shared secrets. Not used for signatures or authentication.

---

## Threat Model

roXac protects locally stored history against offline attackers:

- Lost or stolen storage devices
- Offline password guessing against `auth.hash`
- Unauthorised access to encrypted files
- File tampering (detected by AES-256-GCM authentication)

### Out of Scope

- Malware executing on the local machine
- Memory inspection while the application is running
- Hardware or operating system compromise
- Weak or guessed passwords