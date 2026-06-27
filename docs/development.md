# Development

This document covers setting up a local development environment, running tests, and project conventions.

---

## Setup

Clone the repository:

```bash
git clone https://github.com/LakshitSinghBishtTM/roXac.git
cd roXac
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install in editable mode with development dependencies:

```bash
pip install -e ".[dev]"
```

`liboqs` must be installed before running the project or tests. See [`installation.md`](installation.md).

---

## Running Tests

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=roxac --cov-report=term-missing
```

Cryptographic tests require a working `liboqs` installation and are skipped automatically if unavailable.

---

## Source Modules

```
auth.py         Password hashing and key derivation
calc.py         Calculator logic
cli.py          Command-line interface and routing
config.py       Configuration and filesystem management
constants.py    Project constants
crypto.py       Cryptographic operations
exceptions.py   Custom exception hierarchy
history.py      Encrypted history I/O
```

---

## Coding Conventions

- Use type hints.
- Write docstrings on non-trivial functions.
- Keep functions focused on one task.
- Raise project-specific exceptions; do not let library exceptions leak into higher layers.
- Avoid adding dependencies unless clearly necessary.

---

## Testing Philosophy

The test suite verifies every major component independently. When correcting a bug, update or add tests to prevent regressions.

The project is feature-complete. The primary purpose of the test suite is long-term stability, not supporting new feature development.

---

## Dependencies

**Runtime:** `argon2-cffi`, `cryptography`, `liboqs-python`

**Development:** `pytest`, `pytest-cov`