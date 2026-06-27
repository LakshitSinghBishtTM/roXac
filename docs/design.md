# Design

This document explains the reasoning behind roXac's design decisions.

---

# Simplicity and Small Scope

roXac intentionally implements only the four basic arithmetic operations.

* Addition (`+`)
* Subtraction (`-`)
* Multiplication (`\*` or `x`)
* Division (`/`)

No scientific functions, expression parsing, variables, or graphing capabilities are supported or planned.

Keeping the feature set small allows the implementation to remain focused, maintainable, and easy to understand.

Real men use first principles along with 4 basic operations
to derive advanced values anyway.

---

# Local-Only Operation

roXac operates entirely offline.
No internet connection is required.
No telemetry is collected.
No cloud services are used.

All calculations, configuration, and encrypted history remain on the local machine.

---

# Full-Precision Arithmetic

All arithmetic is performed using Python's `Decimal` type.

This avoids many of the rounding issues associated with binary floating-point arithmetic and preserves decimal precision where possible.

---

# Encrypted History

Calculation history is encrypted by default.

Although a calculator does not normally require encrypted storage, roXac treats local history as private user data.

Protecting stored history also provides a practical demonstration of the project's cryptographic architecture.

---

# Modular Architecture

Each module performs one primary task.

For example:

* `calc.py` performs arithmetic.
* `crypto.py` performs cryptographic operations.
* `auth.py` manages authentication.
* `history.py` manages encrypted history.
* `config.py` manages persistent configuration.

This separation keeps responsibilities clear and simplifies testing.

---

# Explicit Error Handling

roXac uses project-specific exception classes instead of exposing implementation-specific exceptions to higher layers.

This provides:

* Consistent error reporting
* Cleaner command-line output
* Better separation between implementation details and user interaction

---