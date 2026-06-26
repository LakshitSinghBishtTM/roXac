"""
Configuration and app directory management.
Owns everything under ~/.roxac/: reads, writes, and first-run initialisation.
"""

import base64
import json
import os
from pathlib import Path

from .constants import (
    APP_DIR,
    AUTH_FILE,
    CIPHER,
    CONFIG_FILE,
    KDF,
    KEM_ALGORITHM,
    KEM_PRIVATE_KEY_FILE,
    KEM_PUBLIC_KEY_FILE,
    VERSION,
)
from .exceptions import ConfigError


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_app_dir() -> Path:
    return Path(APP_DIR).expanduser()


def is_configured() -> bool:
    """True if first-run setup has been completed."""
    return (get_app_dir() / CONFIG_FILE).exists()


# ---------------------------------------------------------------------------
# config.json
# ---------------------------------------------------------------------------

def get_config() -> dict:
    try:
        with open(get_app_dir() / CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as exc:
        raise ConfigError(f"Could not read config: {exc}") from exc


def save_config(config: dict) -> None:
    try:
        with open(get_app_dir() / CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as exc:
        raise ConfigError(f"Could not write config: {exc}") from exc


def get_master_key_salt() -> bytes:
    config = get_config()
    try:
        return base64.b64decode(config["master_key_salt"])
    except Exception as exc:
        raise ConfigError(f"Could not read master key salt: {exc}") from exc


def increment_history_count() -> None:
    config = get_config()
    config["history_entries"] = config.get("history_entries", 0) + 1
    save_config(config)


def reset_history_count() -> None:
    config = get_config()
    config["history_entries"] = 0
    save_config(config)


# ---------------------------------------------------------------------------
# auth.hash
# ---------------------------------------------------------------------------

def get_auth_hash() -> str:
    try:
        return (get_app_dir() / AUTH_FILE).read_text().strip()
    except Exception as exc:
        raise ConfigError(f"Could not read auth hash: {exc}") from exc


# ---------------------------------------------------------------------------
# ML-KEM key files
# ---------------------------------------------------------------------------

def get_public_key() -> bytes:
    try:
        return (get_app_dir() / KEM_PUBLIC_KEY_FILE).read_bytes()
    except Exception as exc:
        raise ConfigError(f"Could not read public key: {exc}") from exc


def get_encrypted_private_key() -> bytes:
    try:
        return (get_app_dir() / KEM_PRIVATE_KEY_FILE).read_bytes()
    except Exception as exc:
        raise ConfigError(f"Could not read encrypted private key: {exc}") from exc


# ---------------------------------------------------------------------------
# First-run initialisation
# ---------------------------------------------------------------------------

def initialize(
    password_hash: str,
    public_key: bytes,
    encrypted_private_key: bytes,
    master_key_salt: bytes,
) -> None:
    """
    Create ~/.roxac/ and write all initial files.
    Called exactly once during first-run setup.
    """
    app_dir = get_app_dir()
    try:
        app_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except Exception as exc:
        raise ConfigError(f"Could not create app directory: {exc}") from exc

    config = {
        "version": VERSION,
        "kem_algorithm": KEM_ALGORITHM,
        "cipher": CIPHER,
        "kdf": KDF,
        "history_entries": 0,
        "master_key_salt": base64.b64encode(master_key_salt).decode("ascii"),
    }
    save_config(config)

    _write(app_dir / AUTH_FILE, password_hash.encode(), mode=0o600)
    _write(app_dir / KEM_PUBLIC_KEY_FILE, public_key, mode=0o644)
    _write(app_dir / KEM_PRIVATE_KEY_FILE, encrypted_private_key, mode=0o600)


def _write(path: Path, data: bytes, mode: int) -> None:
    path.write_bytes(data)
    os.chmod(path, mode)