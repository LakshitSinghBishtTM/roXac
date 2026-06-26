"""Tests for crypto.py i.e., ML-KEM-768 + AES-256-GCM.
Skipped automatically if liboqs is not installed.
"""

import os
import pytest

oqs = pytest.importorskip("oqs", reason="liboqs not installed; skipping ML-KEM tests")

from roxac.crypto import (
    aes_gcm_decrypt,
    aes_gcm_encrypt,
    decapsulate,
    decrypt_history_entry,
    decrypt_with_master_key,
    encapsulate,
    encrypt_history_entry,
    encrypt_with_master_key,
    generate_keypair,
)
from roxac.exceptions import HistoryDecryptionError


class TestAESGCM:
    def test_roundtrip(self):
        key = os.urandom(32)
        plaintext = b"roXac test payload"
        nonce, ct = aes_gcm_encrypt(key, plaintext)
        assert aes_gcm_decrypt(key, nonce, ct) == plaintext

    def test_wrong_key_raises(self):
        key = os.urandom(32)
        nonce, ct = aes_gcm_encrypt(key, b"data")
        with pytest.raises(HistoryDecryptionError):
            aes_gcm_decrypt(os.urandom(32), nonce, ct)

    def test_tampered_ciphertext_raises(self):
        key = os.urandom(32)
        nonce, ct = aes_gcm_encrypt(key, b"data")
        tampered = ct[:-1] + bytes([ct[-1] ^ 0xFF])
        with pytest.raises(HistoryDecryptionError):
            aes_gcm_decrypt(key, nonce, tampered)

    def test_each_encryption_unique(self):
        key = os.urandom(32)
        n1, c1 = aes_gcm_encrypt(key, b"same")
        n2, c2 = aes_gcm_encrypt(key, b"same")
        assert n1 != n2  # Fresh nonce each time


class TestMasterKeyCrypto:
    def test_roundtrip(self):
        key = os.urandom(32)
        data = b"private key bytes"
        assert decrypt_with_master_key(encrypt_with_master_key(data, key), key) == data

    def test_wrong_key_raises(self):
        key = os.urandom(32)
        encrypted = encrypt_with_master_key(b"data", key)
        with pytest.raises(HistoryDecryptionError):
            decrypt_with_master_key(encrypted, os.urandom(32))


class TestKEM:
    def setup_method(self):
        self.pub, self.priv = generate_keypair()

    def test_keypair_sizes(self):
        assert len(self.pub) == 1184   # ML-KEM-768 public key
        assert len(self.priv) == 2400  # ML-KEM-768 private key

    def test_encap_decap_produces_same_secret(self):
        ct, ss_sender = encapsulate(self.pub)
        ss_receiver = decapsulate(self.priv, ct)
        assert ss_sender == ss_receiver

    def test_shared_secret_is_32_bytes(self):
        _, ss = encapsulate(self.pub)
        assert len(ss) == 32

    def test_each_encapsulation_unique(self):
        ct1, ss1 = encapsulate(self.pub)
        ct2, ss2 = encapsulate(self.pub)
        assert ct1 != ct2
        assert ss1 != ss2


class TestHistoryEntryCrypto:
    def setup_method(self):
        self.pub, self.priv = generate_keypair()

    def test_roundtrip(self):
        entry = "$ roxac 123 + 456\n> 579"
        blob = encrypt_history_entry(self.pub, entry)
        result, _ = decrypt_history_entry(self.priv, blob, 0)
        assert result == entry

    def test_each_encryption_unique(self):
        entry = "$ roxac 1 + 1\n> 2"
        assert encrypt_history_entry(self.pub, entry) != encrypt_history_entry(self.pub, entry)

    def test_offset_advances_to_end(self):
        blob = encrypt_history_entry(self.pub, "test entry")
        _, new_offset = decrypt_history_entry(self.priv, blob, 0)
        assert new_offset == len(blob)

    def test_wrong_private_key_raises(self):
        _, wrong_priv = generate_keypair()
        blob = encrypt_history_entry(self.pub, "secret")
        with pytest.raises(HistoryDecryptionError):
            decrypt_history_entry(wrong_priv, blob, 0)