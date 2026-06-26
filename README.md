# roXaC

roXac is a simple pip-installable CLI calculator.

---

## Features

- Simple and easy to use
- Full-precision arithmetic
- Supports all 4 basic Operators: `+`, `-`, `*`, and `/`
- Local and offline, no internet required
- Consistent and structured output tags 

---

## Usage

### Calculate

```
roxac <num1> <operator> <num2>
```

```
$ roxac 36 + 33
> 69

$ roxac 7 x 7
> 49
```

---

### View History

```
$ roxac history
> Please enter the password
  Password:
> [info] Calculation history:
  ----------------------------------------------------------------------------------------------------
$ roxac 36 + 33
> 69

$ roxac 7 x 7
> 49
  ----------------------------------------------------------------------------------------------------
```

---

### Clear History

```
$ roxac sudo rm -rf / --no-preserve-root
> Please enter the password
> Password:
> [done] History cleared.
```

---

### Status

```
$ roxac status
> [info] roXac Status
  ----------------------------------------------------------------------------------------------------
> Algorithm      : ML-KEM-768
> Cipher         : AES-256-GCM
> Password KDF   : Argon2id
> History entries: 2
> Version        : 1.0.0
  ----------------------------------------------------------------------------------------------------
```

---

## Installation

```bash
pip install roxac
```

See [`docs/installation.md`](docs/installation.md) for detailed installation.

---

## Project Structure

```
roxac/
|-- src/roxac/
|   |-- auth.py
|   |-- calc.py
|   |-- cli.py
|   |-- config.py
|   |-- constants.py
|   |-- crypto.py
|   |-- exceptions.py
|   |-- history.py
|-- tests/
|   |-- test_auth.py
|   |-- test_calc.py
|   |-- test_crypto.py
|   |-- test_history.py
|-- README.md
|-- LICENSE
|-- pyproject.toml
```

---

## Project Availability

roXac is distributed across multiple platforms to reduce reliance on any single provider.

| Platform          | URL                                               |
|-------------------|---------------------------------------------------|
| GitHub (primary)  |	https://github.com/LakshitSinghBishtTM/roXac      |
| GitLab	          | https://gitlab.com/LakshitSinghBishtTM/roXac      |
| Codeberg          |	https://codeberg.org/lakshitsinghbishttm/roXac    |
| Bitbucket	        | https://bitbucket.org/lakshitsinghbishttm/roXac   |
| Gitea	            | https://gitea.com/LakshitSinghBishtTM/roXac       |
| Sourceforge	      | https://sourceforge.net/projects/roXac            |

---

## Security Stack

roXac uses the following security stack for protecting local history.

| Layer                       | Technology                                          |
|-----------------------------|-----------------------------------------------------|
| Password hashing            | Argon2id                                            |
| Key derivation (master key) | Argon2id (raw output, 32 bytes)                     |
| Key encapsulation           | ML-KEM-768 (NIST FIPS 203, via `liboqs-python`)     |
| Private key protection      | AES-256-GCM (encrypted with master key)             |
| History encryption          | AES-256-GCM (key derived from ML-KEM shared secret) |

---

## License

roXac is licensed under the **GNU General Public License v3.0**.  
See [`LICENSE`](LICENSE) for the full text.

---