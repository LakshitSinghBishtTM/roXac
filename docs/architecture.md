# Architecture

This document describes the internal structure of roXac and how its components interact.

---

## Project Layout

```
src/roxac/
├── auth.py
├── calc.py
├── cli.py
├── config.py
├── constants.py
├── crypto.py
├── exceptions.py
├── history.py
└── __init__.py
```

---

## Module Responsibilities

### `cli.py`
Entry point. Parses arguments, routes commands, handles first-time setup, and manages user interaction. Contains no calculator logic or cryptographic implementation.

### `calc.py`
Arithmetic. Parses numeric input, validates operators, performs calculations using Python's `Decimal`, and formats output. Supported operators: `+`, `-`, `*`, `x`, `/`.

### `auth.py`
Authentication and key derivation. Handles password hashing, password verification, master key derivation, and salt generation. Never performs encryption itself.

### `crypto.py`
Cryptographic primitives. ML-KEM-768 key generation, encapsulation, decapsulation, AES-256-GCM encryption, and decryption. All cryptographic operations are isolated here.

### `history.py`
Encrypted history storage. Encrypts and appends entries, reads and decrypts history, clears history. Every entry is independently encrypted.

### `config.py`
Configuration and filesystem management. Creates the application directory, reads and writes configuration files, manages history counters, and handles key material storage. All filesystem interaction outside encrypted history is centralised here.

### `constants.py`
Single source of truth for all project constants: version, algorithm names, Argon2id parameters, file names, and default values.

### `exceptions.py`
Project-specific exception hierarchy. Prevents implementation-specific exceptions from leaking into higher layers and provides consistent error reporting.

---

## Data Flow

A typical calculation:

```
User input
    │
    ▼
cli.py          (argument parsing, routing)
    │
    ▼
calc.py         (arithmetic)
    │
    ▼
Result printed
    │
    ▼
history.py      (encrypt entry)
    │
    ▼
crypto.py       (ML-KEM + AES-256-GCM)
    │
    ▼
history.enc
```

---

## First-Time Setup Flow

```
User sets password
    │
    ▼
Generate ML-KEM-768 keypair
    │
    ▼
Hash password (Argon2id)
    │
    ▼
Derive master key (Argon2id)
    │
    ▼
Encrypt private key (AES-256-GCM)
    │
    ▼
Write ~/.roxac/
```

Occurs once. Subsequent runs reuse stored configuration.

---

## Storage Layout

```
~/.roxac/
├── config.json       # Algorithm metadata, history entry count
├── auth.hash         # Argon2id password hash
├── kem_public.key    # ML-KEM-768 public key (plaintext)
├── kem_private.enc   # ML-KEM-768 private key (AES-256-GCM encrypted)
└── history.enc       # Encrypted history entries
```