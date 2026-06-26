"""
Encrypted history I/O.

Entries are appended as self-delimiting binary blobs (no outer length prefix
needed, each blob encodes its own component lengths). Reading iterates
through the file using byte offsets until EOF.

Write path (no password required):
    encrypt_history_entry(public_key, entry) --> bytes --> append to history.enc

Read path (password required):
    read all bytes --> iterate decrypt_history_entry(private_key, data, offset)
"""

from pathlib import Path

from .config import get_app_dir
from .constants import HISTORY_FILE
from .crypto import encrypt_history_entry, decrypt_history_entry
from .exceptions import HistoryDecryptionError, HistoryEncryptionError


def _history_path() -> Path:
    return get_app_dir() / HISTORY_FILE


def append_entry(entry: str, public_key: bytes) -> None:
    """
    Encrypt and append a single history entry.
    No password required — uses the ML-KEM public key only.

    Raises:
        HistoryEncryptionError: if encryption fails.
    """
    encrypted = encrypt_history_entry(public_key, entry)
    with open(_history_path(), "ab") as f:
        f.write(encrypted)


def read_all_entries(private_key: bytes) -> list[str]:
    """
    Decrypt and return all history entries in order.

    Args:
        private_key: Decrypted ML-KEM-768 private key bytes.

    Returns:
        List of plaintext entry strings, oldest first.

    Raises:
        HistoryDecryptionError: if any entry fails to decrypt.
    """
    path = _history_path()
    if not path.exists() or path.stat().st_size == 0:
        return []

    data = path.read_bytes()
    entries: list[str] = []
    offset = 0

    while offset < len(data):
        entry, offset = decrypt_history_entry(private_key, data, offset)
        entries.append(entry)

    return entries


def clear_history() -> None:
    """
    Delete history.enc.
    Caller is responsible for verifying the password before calling this.
    """
    path = _history_path()
    if path.exists():
        path.unlink()