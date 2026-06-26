"""
Cryptographic operations.
Wraps liboqs ML-KEM-768 (key encapsulation) and AES-256-GCM (authenticated
encryption) into a clean, roXac-specific API.

History entry binary format (per entry):
  [4 bytes big-endian : KEM ciphertext length ]
  [N bytes            : ML-KEM-768 ciphertext ]
  [12 bytes           : AES-GCM nonce         ]
  [4 bytes big-endian : AES ciphertext length ]
  [M bytes            : AES ciphertext + tag  ]

Each entry carries its own KEM encapsulation so the history file can be
appended to without decrypting existing entries (i.e., no password needed
to add a new calculation to history).
"""

import os
import struct

import oqs
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .constants import KEM_ALGORITHM, AES_KEY_SIZE, AES_NONCE_SIZE
from .exceptions import HistoryDecryptionError, HistoryEncryptionError


# ---------------------------------------------------------------------------
# ML-KEM-768 operations
# ---------------------------------------------------------------------------

def generate_keypair() -> tuple[bytes, bytes]:
    """
    Generate an ML-KEM-768 keypair.

    Returns:
        (public_key, private_key) as raw bytes.
        ML-KEM-768 sizes: public_key = 1184 B, private_key = 2400 B.
    """
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        public_key = kem.generate_keypair()
        private_key = kem.export_secret_key()
    return public_key, private_key


def encapsulate(public_key: bytes) -> tuple[bytes, bytes]:
    """
    Encapsulate a shared secret to a public key (sender side).

    Returns:
        (ciphertext, shared_secret)
        ML-KEM-768: ciphertext = 1088 B, shared_secret = 32 B.
    """
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        ciphertext, shared_secret = kem.encap_secret(public_key)
    return ciphertext, shared_secret


def decapsulate(private_key: bytes, ciphertext: bytes) -> bytes:
    """
    Decapsulate a ciphertext with a private key (receiver side).

    Returns:
        shared_secret (32 bytes).
    """
    with oqs.KeyEncapsulation(KEM_ALGORITHM, secret_key=private_key) as kem:
        shared_secret = kem.decap_secret(ciphertext)
    return shared_secret


# ---------------------------------------------------------------------------
# AES-256-GCM operations
# ---------------------------------------------------------------------------

def aes_gcm_encrypt(key: bytes, plaintext: bytes) -> tuple[bytes, bytes]:
    """
    Encrypt plaintext with AES-256-GCM using a random nonce.

    Args:
        key:       32-byte key (only first AES_KEY_SIZE bytes are used).
        plaintext: Arbitrary bytes to encrypt.

    Returns:
        (nonce, ciphertext_with_tag): nonce is 12 bytes, ciphertext
        includes the 16-byte GCM authentication tag appended by the
        cryptography library.
    """
    nonce = os.urandom(AES_NONCE_SIZE)
    aesgcm = AESGCM(key[:AES_KEY_SIZE])
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def aes_gcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt and verify an AES-256-GCM ciphertext.

    Raises:
        HistoryDecryptionError: on authentication failure or any crypto error.
    """
    aesgcm = AESGCM(key[:AES_KEY_SIZE])
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise HistoryDecryptionError(f"AES-GCM decryption failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Master-key encryption (used for the ML-KEM private key at rest)
# ---------------------------------------------------------------------------

def encrypt_with_master_key(data: bytes, master_key: bytes) -> bytes:
    """
    Encrypt arbitrary bytes with a 32-byte master key using AES-256-GCM.

    Returns:
        nonce (12 B) || ciphertext_with_tag
    """
    nonce, ciphertext = aes_gcm_encrypt(master_key, data)
    return nonce + ciphertext


def decrypt_with_master_key(encrypted_data: bytes, master_key: bytes) -> bytes:
    """
    Decrypt data produced by encrypt_with_master_key.

    Raises:
        HistoryDecryptionError: on authentication failure.
    """
    nonce = encrypted_data[:AES_NONCE_SIZE]
    ciphertext = encrypted_data[AES_NONCE_SIZE:]
    return aes_gcm_decrypt(master_key, nonce, ciphertext)


# ---------------------------------------------------------------------------
# Per-entry history encryption (ML-KEM + AES-256-GCM)
# ---------------------------------------------------------------------------

def encrypt_history_entry(public_key: bytes, entry: str) -> bytes:
    """
    Encrypt a single history entry string.

    Uses ML-KEM encapsulation to derive a one-time AES key; that key is then
    used to AES-256-GCM encrypt the entry. No password is required — only
    the public key.

    Binary layout:
        [4 B: kem_ct_len][kem_ct][12 B: nonce][4 B: aes_ct_len][aes_ct+tag]
    """
    plaintext = entry.encode("utf-8")
    try:
        kem_ct, shared_secret = encapsulate(public_key)
        nonce, aes_ct = aes_gcm_encrypt(shared_secret[:AES_KEY_SIZE], plaintext)
    except Exception as exc:
        raise HistoryEncryptionError(f"Failed to encrypt history entry: {exc}") from exc

    return (
        struct.pack(">I", len(kem_ct))
        + kem_ct
        + nonce
        + struct.pack(">I", len(aes_ct))
        + aes_ct
    )


def decrypt_history_entry(
    private_key: bytes, data: bytes, offset: int = 0
) -> tuple[str, int]:
    """
    Decrypt a single history entry from a binary blob at the given byte offset.

    Args:
        private_key: Decrypted ML-KEM-768 private key.
        data:        Full binary content of history.enc.
        offset:      Byte offset to start reading from.

    Returns:
        (entry_string, new_offset)  - new_offset points past this entry.

    Raises:
        HistoryDecryptionError: on any decryption or integrity failure.
    """
    try:
        # KEM ciphertext
        kem_ct_len = struct.unpack(">I", data[offset : offset + 4])[0]
        offset += 4
        kem_ct = data[offset : offset + kem_ct_len]
        offset += kem_ct_len

        # AES nonce
        nonce = data[offset : offset + AES_NONCE_SIZE]
        offset += AES_NONCE_SIZE

        # AES ciphertext
        aes_ct_len = struct.unpack(">I", data[offset : offset + 4])[0]
        offset += 4
        aes_ct = data[offset : offset + aes_ct_len]
        offset += aes_ct_len

        # Decapsulate → shared secret → AES decrypt
        shared_secret = decapsulate(private_key, kem_ct)
        plaintext = aes_gcm_decrypt(shared_secret[:AES_KEY_SIZE], nonce, aes_ct)

        return plaintext.decode("utf-8"), offset

    except HistoryDecryptionError:
        raise
    except Exception as exc:
        raise HistoryDecryptionError(f"Failed to parse history entry: {exc}") from exc