# roXaC

roXac is a simple pip-installable CLI calculator.

---

## Features

- Simple and easy to use
- Fast and accurate
- Full-precision arithmetic
- Supports all 4 basic Operators: `+`, `-`, `*`, and `/`
- Local and offline, no internet required
- Free and open-source
- CLI tags in output making it attractive

---

## Usage

### Calculate

```
roxac <num1> <operator> <num2>
```

```
$ roxac 123 + 456
> 579

$ roxac 7 * 8
> 56

$ roxac 99 + 1
> 100
```

---

### View History

```
$ roxac history
> Please enter the password
  Password:
> 
$ roxac 123 + 456
> 579

$ roxac 7 * 8
> 56

$ roxac 99 + 1
> 100
```

---

### Clear History

```
$ roxac sudo rm -rf / --no-preserve-root
> Please enter the password
  Password:
> [done] History cleared.
```

---

### Status

```
$ roxac status
> [info] roXac Status
--------------------------------------------------
> Algorithm      : ML-KEM-768
> Cipher         : AES-256-GCM
> Password KDF   : Argon2id
> History entries: 47
> Version        : 1.0.0

--------------------------------------------------
```

---

## Installation

### Prerequisites

roXac uses [`liboqs-python`](https://github.com/open-quantum-safe/liboqs-python), the official Python binding for the Open Quantum Safe library. Pre-built wheels are available for common platforms (Linux x86_64, macOS, Windows).

If your platform doesn't have a pre-built wheel, you'll need to build liboqs from source first:

```
# Ubuntu / Debian
sudo apt-get install -y cmake ninja-build libssl-dev
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs
cmake -GNinja -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=/usr/local .
ninja && sudo ninja install && sudo ldconfig
```

### Install roXac

```
pip install roxac
```

---

## Development

```
git clone https://github.com/yourusername/roxac.git
cd roxac
pip install -e ".[dev]"
pytest
```

### Running tests

```
pytest --cov=roxac --cov-report=term-missing
```

---

## Project Structure

```
roxac/
├── src/roxac/
│   ├── cli.py          # Entry point and command routing
│   ├── calc.py         # Calculator logic
│   ├── crypto.py       # ML-KEM-768 + AES-256-GCM
│   ├── auth.py         # Argon2id
│   ├── history.py      # Calculation History I/O
│   ├── config.py       # ~/.roxac/ management
│   ├── constants.py    # All constants in one place
│   └── exceptions.py   # Custom exception hierarchy
└── tests/
```

---

## Security Stack

| Layer                       | Technology                                          |
|-----------------------------|-----------------------------------------------------|
| Password hashing            | Argon2id                                            |
| Key derivation (master key) | Argon2id (raw output, 32 bytes)                     |
| Key encapsulation           | ML-KEM-768 (NIST FIPS 203, via `liboqs-python`)     |
| Private key protection      | AES-256-GCM (encrypted with master key)             |
| History encryption          | AES-256-GCM (key derived from ML-KEM shared secret) |

History entries are independently encrypted with the ML-KEM-768 public key. This means:
- Writing history never requires your password
- Reading or clearing history always requires your password
- Changing your password does not re-encrypt history (the keypair stays the same; only the encrypted private key wrapper changes)

---

## Storage Layout

```
~/.roxac/
├── config.json         # Algorithm metadata, entry count
├── auth.hash           # Argon2id password hash
├── kem_public.key      # ML-KEM-768 public key (plaintext)
├── kem_private.enc     # ML-KEM-768 private key (AES-256-GCM encrypted)
└── history.enc         # Encrypted history entries (length-prefixed binary)
```

---

## License

roXac is licensed under the **GNU General Public License v3.0**.  
See [LICENSE](LICENSE) for the full text.

---
