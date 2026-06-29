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


class PartialHistoryError(HistoryDecryptionError):
    """
    Raised when history.enc contains a corrupted or truncated entry, but one
    or more earlier entries were decrypted successfully before the failure."""

    def __init__(self, entries: list[str], cause: Exception):
        count = len(entries)
        super().__init__(
            f"{count} entr{'y' if count == 1 else 'ies'} recovered; "
            f"history is corrupted or truncated beyond that point ({cause})"
        )
        self.entries = entries
        self.cause = cause


class FirstRunRequired(RoXacError):
    """Raised when roXac is used before first-run initialisation."""
    pass


class HistoryEncryptionError(RoXacError):
    """Raised when encrypting a history entry fails."""
    pass


class ConfigError(RoXacError):
    """Raised when there is an issue reading or writing configuration."""
    pass