"""
Tests for config.py app directory management and first-run initialisation.
"""

import pytest

from roxac import config
from roxac.exceptions import ConfigError


@pytest.fixture
def app_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "get_app_dir", lambda: tmp_path)
    return tmp_path


def _initialize(**overrides):
    defaults = dict(
        password_hash="roasted-in-fire",
        public_key=b"made-from-clay",
        encrypted_private_key=b"made-from-gold",
        master_key_salt=b"table-salt",
    )
    defaults.update(overrides)
    config.initialize(
        defaults["password_hash"],
        defaults["public_key"],
        defaults["encrypted_private_key"],
        defaults["master_key_salt"],
    )


class TestIsConfigured:
    def test_false_before_initialize(self, app_dir):
        assert config.is_configured() is False

    def test_true_after_initialize(self, app_dir):
        _initialize()
        assert config.is_configured() is True


class TestInitializeWriteOrder:
    def test_config_json_is_written_last(self, app_dir, monkeypatch):
        """
        config.json is the file is_configured() checks. It must be written
        last: if setup is interrupted (crash, power loss, disk full)
        anywhere before that final write, is_configured() must still
        correctly report False, rather than reporting "configured" while
        auth.hash / the key files are actually missing.
        """
        write_order = []

        original_write = config._write
        original_save_config = config.save_config

        def tracking_write(path, data, mode):
            write_order.append(path.name)
            return original_write(path, data, mode)

        def tracking_save_config(cfg):
            write_order.append("config.json")
            return original_save_config(cfg)

        monkeypatch.setattr(config, "_write", tracking_write)
        monkeypatch.setattr(config, "save_config", tracking_save_config)

        _initialize()

        assert write_order[-1] == "config.json"
        assert "auth.hash" in write_order
        assert "kem_public.key" in write_order
        assert "kem_private.enc" in write_order

    def test_interrupted_setup_leaves_is_configured_false(self, app_dir, monkeypatch):
        """
        Simulates a crash that happens after the key files are written but
        before config.json. is_configured() must report False so a later
        run retries setup cleanly, instead of looking configured while
        auth.hash/keys are present but config.json (and therefore the
        master key salt) is not.
        """
        def boom(cfg):
            # save_config() wraps underlying errors in ConfigError; mimic
            # that here rather than re-testing save_config's own wrapping.
            raise ConfigError("disk full")

        monkeypatch.setattr(config, "save_config", boom)

        with pytest.raises(ConfigError):
            _initialize()

        assert config.is_configured() is False
        # The key files that were written before the crash are now orphaned
        # on disk, but that's fine, is_configured() is False, so a retry
        # will simply overwrite them.
        assert (app_dir / "auth.hash").exists()


class TestHistoryCounters:
    def test_increment_and_reset(self, app_dir):
        _initialize()
        config.increment_history_count()
        config.increment_history_count()
        assert config.get_config()["history_entries"] == 2

        config.reset_history_count()
        assert config.get_config()["history_entries"] == 0


class TestMissingFilesRaiseConfigError:
    def test_get_auth_hash_missing(self, app_dir):
        with pytest.raises(ConfigError):
            config.get_auth_hash()

    def test_get_public_key_missing(self, app_dir):
        with pytest.raises(ConfigError):
            config.get_public_key()

    def test_get_encrypted_private_key_missing(self, app_dir):
        with pytest.raises(ConfigError):
            config.get_encrypted_private_key()

    def test_get_config_missing(self, app_dir):
        with pytest.raises(ConfigError):
            config.get_config()
