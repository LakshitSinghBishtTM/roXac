"""
Tests for cli.py error classification in the authenticated-command path.

_load_secret_key() must raise AuthenticationError for a wrong password but
ConfigError for a missing/corrupted installation (missing auth.hash,
missing kem_private.enc, etc.), so that cmd_history()/cmd_clear() can tell
the two apart instead of reporting every failure as "Wrong password".

None of this exercises real ML-KEM (_load_secret_key never touches the KEM
keys' cryptographic validity, only Argon2id + AES-GCM), so plain placeholder
bytes are used for the public/private key material and no liboqs
installation is required to run these tests.
"""

import pytest

from roxac import auth, config, crypto
from roxac.cli import _load_secret_key
from roxac.exceptions import AuthenticationError, ConfigError

PASSWORD = "Why are you looking at this?"


@pytest.fixture
def configured_app_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "get_app_dir", lambda: tmp_path)

    public_key = b"secret-key"
    secret_key = b"public-key"

    salt = auth.generate_master_key_salt()
    master_key = auth.derive_master_key(PASSWORD, salt)
    encrypted_private_key = crypto.encrypt_with_master_key(secret_key, master_key)
    password_hash = auth.hash_password(PASSWORD)

    config.initialize(password_hash, public_key, encrypted_private_key, salt)
    return tmp_path


class TestLoadSecretKey:
    def test_correct_password_succeeds(self, configured_app_dir):
        assert isinstance(_load_secret_key(PASSWORD), bytes)

    def test_wrong_password_raises_authentication_error(self, configured_app_dir):
        with pytest.raises(AuthenticationError):
            _load_secret_key("not the password")

    def test_missing_auth_file_raises_config_error_not_authentication_error(
        self, configured_app_dir
    ):
        (configured_app_dir / "auth.hash").unlink()
        with pytest.raises(ConfigError):
            _load_secret_key(PASSWORD)

    def test_missing_private_key_file_raises_config_error(self, configured_app_dir):
        (configured_app_dir / "kem_private.enc").unlink()
        with pytest.raises(ConfigError):
            _load_secret_key(PASSWORD)

    def test_corrupted_config_json_raises_config_error(self, configured_app_dir):
        (configured_app_dir / "config.json").write_text("{not valid json")
        with pytest.raises(ConfigError):
            _load_secret_key(PASSWORD)
