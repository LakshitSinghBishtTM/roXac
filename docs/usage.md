# Usage

---

## Calculate

```
roxac <number> <operator> <number>
```

```bash
roxac 125 + 375
> 500
```

---

## Operators

| Operator | Operation      |
| -------- | -------------- |
| `+`      | Addition       |
| `-`      | Subtraction    |
| `x`      | Multiplication |
| `*`      | Multiplication |
| `/`      | Division       |

Use `x` for multiplication. Bare `*` is expanded by the shell before roXac receives it.

```bash
roxac 10 x 10     # recommended
roxac 10 \* 10    # also works
```

---

## Examples

```bash
roxac 10 + 10
> 20

roxac 50 - 17
> 33

roxac 25 x 4
> 100

roxac 144 / 12
> 12

roxac 1 / 3
> 0.33333333333333333333333333333333333333333333333333
```

---

## First Run

The first calculation triggers one-time setup. You will be prompted to create a master password.

Setup generates an ML-KEM-768 key pair, hashes the password, and creates `~/.roxac/`. This happens once.

---

## History

```bash
roxac history
```

Prompts for password, then displays all past calculations in order.

---

## Clear History

```bash
roxac sudo rm -rf / --no-preserve-root
```

Prompts for password, then deletes encrypted history. Configuration and keys are not affected.

---

## Status

```bash
roxac status
```

Displays algorithm, cipher, KDF, history entry count, and version. No password required.

---

## Help and Version

```bash
roxac             # banner
roxac --help      # usage summary
roxac --version   # version number
```

---

## Errors

roXac prints a descriptive error and exits without modifying history when it encounters:

- Invalid operator
- Invalid numeric input
- Division by zero
- Incorrect password