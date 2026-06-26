"""
Authentication.
Handles password hashing/verification (Argon2id) and deterministic
master key derivation from a password + salt.

Two separate Argon2id operations are intentionally used:
  1. hash_password / verify_password  : password verification (random salt, stored hash)
  2. derive_master_key                : key derivation (fixed salt stored in config.json)

Keeping them separate means a password change can re-derive the master key
from a new salt without re-generating the ML-KEM keypair.
"""

import os

import argon2
import argon2.low_level as _argon2_low

from .constants import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LEN,
    ARGON2_SALT_LEN,
)

# Shared PasswordHasher instance (thread-safe, stateless after construction).
_ph = argon2.PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LEN,
    salt_len=ARGON2_SALT_LEN,
)


def hash_password(password: str) -> str:
    """
    Hash a password with Argon2id.
    Returns a self-contained hash string (includes algorithm, params, salt).
    Safe to store directly to disk.
    """
    return _ph.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against its stored Argon2id hash.
    Returns True on success, False on mismatch or any error.
    Never raises.
    """
    try:
        return _ph.verify(stored_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        return False
    except Exception:
        return False


def derive_master_key(password: str, salt: bytes) -> bytes:
    """
    Derive a master key from a password and salt using Argon2id.

    This is deterministic: the same password + salt always produces the
    same key. The salt must be stored (in config.json) to allow re-derivation.

    Args:
        password : The user's plaintext password.
        salt     : Random salt.

    Returns:
        Key material.
    """
    return _argon2_low.hash_secret_raw(
        password.encode("utf-8"),
        salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=_argon2_low.Type.ID,
    )


def generate_master_key_salt() -> bytes:
    """Generate a cryptographically secure random salt for master key derivation."""
    return os.urandom(ARGON2_SALT_LEN)