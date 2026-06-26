"""
Custom exceptions.
Provides typed errors that abstract over raw crypto/system errors,
so callers never have to interpret what liboqs or the cryptography
library decided to throw at them.
"""


class RoXacError(Exception):
    """Base exception for all roXac errors."""
    pass


class AuthenticationError(RoXacError):
    """Raised when password verification fails."""
    pass


class InvalidExpression(RoXacError):
    """Raised when the calculator expression is malformed or undefined."""
    pass


class HistoryDecryptionError(RoXacError):
    """Raised when history decryption fails (wrong key, tampered data)."""
    pass


class FirstRunRequired(RoXacError):
    """Raised when roXac is used before first-run initialisation."""
    pass


class HistoryEncryptionError(RoXacError):
    """Raised when encrypting a history entry fails."""
    pass


class ConfigError(RoXacError):
    """Raised when there is an issue reading or writing configuration."""
    pass