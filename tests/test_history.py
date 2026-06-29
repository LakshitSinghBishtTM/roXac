"Tests for history.py."

import pytest
from unittest.mock import patch

oqs = pytest.importorskip("oqs", reason="liboqs not installed; skipping history crypto tests")

from roxac.crypto import generate_keypair
from roxac.exceptions import HistoryDecryptionError, PartialHistoryError
from roxac.history import append_entry, clear_history, read_all_entries


@pytest.fixture(scope="module")
def keypair():
    return generate_keypair()


@pytest.fixture
def history_file(tmp_path):
    return tmp_path / "history.enc"


def test_empty_history_returns_empty_list(keypair, history_file):
    _, priv = keypair
    with patch("roxac.history._history_path", return_value=history_file):
        assert read_all_entries(priv) == []


def test_single_entry_roundtrip(keypair, history_file):
    pub, priv = keypair
    entry = "$ roxac 1 + 1\n> 2"
    with patch("roxac.history._history_path", return_value=history_file):
        append_entry(entry, pub)
        assert read_all_entries(priv) == [entry]


def test_multiple_entries_order_preserved(keypair, history_file):
    pub, priv = keypair
    entries = [
        "$ roxac 10 + 20\n> 30",
        "$ roxac 10 / 3\n> 3.33333333333333333333333333333333333333333333333333",
        "$ roxac 7 * 8\n> 56",
    ]
    with patch("roxac.history._history_path", return_value=history_file):
        for e in entries:
            append_entry(e, pub)
        assert read_all_entries(priv) == entries


def test_clear_deletes_file(keypair, history_file):
    pub, _ = keypair
    with patch("roxac.history._history_path", return_value=history_file):
        append_entry("$ roxac 2 + 2\n> 4", pub)
        assert history_file.exists()
        clear_history()
        assert not history_file.exists()


def test_clear_nonexistent_file_does_not_raise(history_file):
    with patch("roxac.history._history_path", return_value=history_file):
        clear_history()  # should not raise


def test_history_file_is_not_plaintext(keypair, history_file):
    pub, _ = keypair
    entry = "$ roxac 42 / 7\n> 6"
    with patch("roxac.history._history_path", return_value=history_file):
        append_entry(entry, pub)
    raw = history_file.read_bytes()
    assert b"42" not in raw
    assert b"roxac" not in raw

class TestPartialHistoryRecovery:

    def test_truncated_trailing_entry_recovers_earlier_entries(self, keypair, history_file):
        pub, priv = keypair
        good_entries = [
            "$ roxac 1 + 1\n> 2",
            "$ roxac 2 + 2\n> 4",
        ]
        with patch("roxac.history._history_path", return_value=history_file):
            for e in good_entries:
                append_entry(e, pub)

            append_entry("$ roxac 3 + 3\n> 6", pub)
            truncated = history_file.read_bytes()[:-5]
            history_file.write_bytes(truncated)

            with pytest.raises(PartialHistoryError) as excinfo:
                read_all_entries(priv)

            assert excinfo.value.entries == good_entries

    def test_fully_corrupted_history_with_nothing_recoverable_raises_plain_error(
        self, keypair, history_file
    ):
        _, priv = keypair
        with patch("roxac.history._history_path", return_value=history_file):
            # Garbage from byte zero -- not even the first entry parses.
            history_file.write_bytes(b"\x00" * 20)

            with pytest.raises(HistoryDecryptionError) as excinfo:
                read_all_entries(priv)

            assert not isinstance(excinfo.value, PartialHistoryError)

    def test_partial_history_error_is_a_history_decryption_error(self, keypair, history_file):
        pub, priv = keypair
        with patch("roxac.history._history_path", return_value=history_file):
            append_entry("$ roxac 1 + 1\n> 2", pub)
            append_entry("$ roxac 9 + 9\n> 18", pub)
            truncated = history_file.read_bytes()[:-3]
            history_file.write_bytes(truncated)

            with pytest.raises(HistoryDecryptionError):
                read_all_entries(priv)