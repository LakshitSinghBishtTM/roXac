"""
CLI entry point.
"""

import getpass
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="oqs")
os.environ["OQS_PYTHON_FAULTHANDLER"] = "0"

from .auth import derive_master_key, generate_master_key_salt, hash_password, verify_password
from .calc import calculate
from .config import (
    get_auth_hash,
    get_config,
    get_encrypted_private_key,
    get_master_key_salt,
    get_public_key,
    increment_history_count,
    initialize,
    is_configured,
    reset_history_count,
)
from .constants import CIPHER, KDF, KEM_ALGORITHM, VERSION
from .crypto import decrypt_with_master_key, encrypt_with_master_key, generate_keypair
from .exceptions import (
    AuthenticationError,
    ConfigError,
    HistoryDecryptionError,
    HistoryEncryptionError,
    InvalidExpression,
)
from .history import append_entry, clear_history, read_all_entries

_CLEAR_ARGS = ["sudo", "rm", "-rf", "/", "--no-preserve-root"]

_BANNER = f"""\
  roXac - A simple CLI calculator
  
  Version : v{VERSION}
  License : GPL-3.0
  Source  : https://github.com/LakshitSinghBishtTM/roXac

  Tip: Run `roxac --help` for available commands.
"""

_USAGE = f"""\

COMMANDS
  roxac <num1> <op> <num2>                          Perform a calculation
  roxac history                                     Show calculation history
  roxac sudo rm -rf / --no-preserve-root            Clear calculation history
  roxac status                                      Show status

OPERATORS
  + - x /

EXAMPLES
  roxac 10 + 10
  roxac 69 x 69
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _prompt_password() -> str:
    print("> Please enter the password")
    return getpass.getpass("> Password: ")


def _load_secret_key(password: str) -> bytes:
    """Verify password and return the decrypted ML-KEM private key."""
    stored_hash = get_auth_hash()
    if not verify_password(password, stored_hash):
        raise AuthenticationError("> [error] Wrong password.")
    salt = get_master_key_salt()
    master_key = derive_master_key(password, salt)
    encrypted_private_key = get_encrypted_private_key()
    return decrypt_with_master_key(encrypted_private_key, master_key)


def _first_run_setup() -> None:
    print("> Welcome to roXac! A simple CLI calculator.")
    print(f"  ----------------------------------------------------------------------------------------------------")
    print("> Set a master password to protect your calculation history.\n")

    while True:
        password = getpass.getpass("> Set password: ")
        if not password:
            print("> [error] Password cannot be empty.\n")
            continue
        confirm = getpass.getpass("> [check] Confirm password: ")
        if password != confirm:
            print("> [error] Passwords do not match. Try again.\n")
            continue
        break

    print("\n> [check] Generating ML-KEM-768 keypair...", end=" ", flush=True)
    public_key, secret_key = generate_keypair()
    print("> [done] Created successfully.")

    salt = generate_master_key_salt()
    master_key = derive_master_key(password, salt)
    encrypted_private_key = encrypt_with_master_key(secret_key, master_key)
    password_hash = hash_password(password)

    initialize(password_hash, public_key, encrypted_private_key, salt)
    print("> [done] Setup complete.")
    print(f"  ----------------------------------------------------------------------------------------------------")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_calculate(num1: str, operator: str, num2: str) -> None:
    if not is_configured():
        _first_run_setup()

    # 'x' can also be used to multiply; normalise for the calculator.
    calc_op = "*" if operator.lower() == "x" else operator

    try:
        result = calculate(num1, calc_op, num2)
    except InvalidExpression as exc:
        print(f"> [error] {exc}")
        sys.exit(1)

    print(f"> {result}")

    # Store original operator in history (preserve what the user typed).
    entry = f"$ roxac {num1} {operator} {num2}\n> {result}"
    try:
        append_entry(entry, get_public_key())
        increment_history_count()
    except (HistoryEncryptionError, ConfigError) as exc:
        print(f"> [error] Warning: could not save to history: {exc}", file=sys.stderr)


def cmd_history() -> None:
    if not is_configured():
        print("> [error] roXac is not set up yet. Run a calculation first.")
        return

    password = _prompt_password()

    try:
        secret_key = _load_secret_key(password)
    except (AuthenticationError, ConfigError):
        print("> [error] Wrong password.")
        sys.exit(1)

    try:
        entries = read_all_entries(secret_key)
    except HistoryDecryptionError as exc:
        print(f"> [error] Error reading history: {exc}")
        sys.exit(1)

    if not entries:
        print("> [error] No history yet.")
        return

    print("> [info] Calculation history:")
    print(f"  ----------------------------------------------------------------------------------------------------")
    print("\n\n".join(entries))
    print(f"  ----------------------------------------------------------------------------------------------------")

def cmd_clear() -> None:
    if not is_configured():
        print("> [error] roXac is not set up yet. Nothing to clear.")
        return

    password = _prompt_password()

    try:
        _load_secret_key(password)   # verification only; key not needed for clear
    except (AuthenticationError, ConfigError):
        print("> [error] Wrong password.")
        sys.exit(1)

    clear_history()
    reset_history_count()
    print("> [done] History cleared.")


def cmd_status() -> None:
    if not is_configured():
        print(f"  ----------------------------------------------------------------------------------------------------")
        print("> [error] Not configured yet.")
        print("> [tip]   Run any calculation to complete first-time setup.")
        print(f"  ----------------------------------------------------------------------------------------------------")
        return

    config = get_config()
    sep = "-" * 100
    print(f"> [info] roXac Status")
    print(f"  {sep}")
    print(f"> Algorithm      : {config.get('kem_algorithm', KEM_ALGORITHM)}")
    print(f"> Cipher         : {config.get('cipher', CIPHER)}")
    print(f"> Password KDF   : {config.get('kdf', KDF)}")
    print(f"> History entries: {config.get('history_entries', 0)}")
    print(f"> Version        : {config.get('version', VERSION)}")
    print(f"  {sep}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(_BANNER)
        return

    if args in (["-h"], ["--help"]):
        print(_USAGE)
        return

    if args in (["-v"], ["--version"]):
        print(f"> roXac v{VERSION}")
        return

    if args == ["history"]:
        cmd_history()
    elif args == _CLEAR_ARGS:
        cmd_clear()
    elif args == ["status"]:
        cmd_status()
    elif len(args) == 3:
        cmd_calculate(args[0], args[1], args[2])
    else:
        print(f"  ----------------------------------------------------------------------------------------------------")
        print(f"> [error] Unrecognised command.")
        print(f"> [tip]   Run `roxac --help` for available commands.")
        print(f"  ----------------------------------------------------------------------------------------------------")
        sys.exit(1)


if __name__ == "__main__":
    main()