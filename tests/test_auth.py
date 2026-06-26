"Tests for auth.py — Argon2id hashing and master key derivation."

import pytest
from roxac.auth import (
    derive_master_key,
    generate_master_key_salt,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_correct_password_verifies(self):
        h = hash_password("hunter2")
        assert verify_password("hunter2", h) is True

    def test_wrong_password_fails(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_hash_is_argon2id_string(self):
        h = hash_password("test")
        assert isinstance(h, str)
        assert "$argon2id$" in h

    def test_two_hashes_of_same_password_differ(self):
        # Different salts → different hashes
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_verify_returns_false_never_raises(self):
        assert verify_password("x", "not_a_valid_hash") is False


class TestMasterKeyDerivation:
    def test_output_is_32_bytes(self):
        salt = generate_master_key_salt()
        key = derive_master_key("password", salt)
        assert len(key) == 32

    def test_deterministic(self):
        salt = generate_master_key_salt()
        assert derive_master_key("pw", salt) == derive_master_key("pw", salt)

    def test_different_salts_produce_different_keys(self):
        k1 = derive_master_key("pw", generate_master_key_salt())
        k2 = derive_master_key("pw", generate_master_key_salt())
        assert k1 != k2

    def test_different_passwords_produce_different_keys(self):
        salt = generate_master_key_salt()
        assert derive_master_key("pw1", salt) != derive_master_key("pw2", salt)

    def test_salt_is_16_bytes(self):
        assert len(generate_master_key_salt()) == 16

    def test_salts_are_random(self):
        assert generate_master_key_salt() != generate_master_key_salt()