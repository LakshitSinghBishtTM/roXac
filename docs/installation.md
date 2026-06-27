# Installation

---

## Requirements

- Python 3.10 or newer
- `pip`
- `liboqs` (native library)

---

## Clone the Repository

```bash
git clone https://github.com/LakshitSinghBishtTM/roXac.git
cd roXac
```

---

## Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install `liboqs`

roXac requires the native `liboqs` library via `liboqs-python`.

**Version requirement:** Install `liboqs` at `0.15.0` to match the `liboqs-python==0.15.0` Python binding.

```bash
sudo apt-get install -y cmake ninja-build libssl-dev

git clone --depth 1 --branch 0.15.0 https://github.com/open-quantum-safe/liboqs.git
cd liboqs
cmake -GNinja \
  -DBUILD_SHARED_LIBS=ON \
  -DOQS_BUILD_ONLY_LIB=ON \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  .
ninja
sudo ninja install
sudo ldconfig
cd ..
```

If `liboqs-python` cannot locate the library at runtime:

```bash
export OQS_INSTALL_PATH=/usr/local
```

---

## Install roXac

Editable install (recommended for development):

```bash
pip install -e ".[dev]"
```

Standard install:

```bash
pip install .
```

---

## Verify

```bash
roxac
roxac 10 + 10
roxac status
```

---

## Common Issues

### `*` expands in the shell

The shell treats bare `*` as a wildcard. Use `x` instead:

```bash
roxac 10 x 10       # recommended
roxac 10 \* 10      # also works
```

### `liboqs not found`

Ensure `liboqs` is installed and run:

```bash
export OQS_INSTALL_PATH=/usr/local
```

### `command not found: roxac`

Ensure the virtual environment is activated and the install completed without errors.