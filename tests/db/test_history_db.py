import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open

# Patch all external dependencies at the top of the module under test
with (
    patch("crowler.db.history_db.json", autospec=True) as mock_json,
    patch("crowler.db.history_db.Path", wraps=Path) as mock_Path,
    patch("crowler.db.history_db.open", create=True) as mock_open_func,
):

    from crowler.db.history_db import HistoryDB


@pytest.fixture
def tmp_history_file(tmp_path):
    file = tmp_path / "history.json"
    file.write_text(json.dumps([{"foo": "bar"}]))
    return file


@pytest.fixture
def history_db(tmp_history_file):
    # Use a simple dict as the snapshot type
    return HistoryDB(
        file_path=tmp_history_file,
        empty={"foo": "empty"},
        normalise=lambda x: {"foo": x["foo"].upper()},
        pretty=lambda x: f"Pretty: {x['foo']}",
    )


def test_init_bootstraps_file_if_not_exists(tmp_path, monkeypatch):
    file_path = tmp_path / "new_history.json"
    # Simulate file not existing
    monkeypatch.setattr(Path, "exists", lambda self: False)
    m = mock_open()
    with patch("crowler.db.history_db.open", m):
        db = HistoryDB(
            file_path=file_path,
            empty={"foo": "empty"},
        )
    m.assert_called_once_with(file_path, "w", encoding="utf-8")
    handle = m()
    handle.write.assert_called()  # Should write initial snapshot


def test_latest_returns_last_snapshot(history_db, tmp_history_file):
    # Add a new snapshot
    history_db.push({"foo": "baz"})
    assert history_db.latest() == {"foo": "BAZ"}


def test_push_appends_and_normalises(history_db, tmp_history_file):
    history_db.push({"foo": "abc"})
    # Should normalise to upper case
    assert history_db.latest() == {"foo": "ABC"}


def test_undo_removes_last_and_returns_true(history_db, tmp_history_file):
    history_db.push({"foo": "one"})
    history_db.push({"foo": "two"})
    assert history_db.latest() == {"foo": "TWO"}
    result = history_db.undo()
    assert result is True
    assert history_db.latest() == {"foo": "ONE"}


def test_undo_returns_false_if_only_one_snapshot(history_db, tmp_history_file):
    # Only the initial snapshot
    assert history_db.undo() is False


def test_clear_resets_to_empty(history_db, tmp_history_file):
    history_db.push({"foo": "something"})
    history_db.clear()
    assert history_db.latest() == {"foo": "empty"}


def test_summary_uses_pretty(history_db, tmp_history_file):
    history_db.push({"foo": "xyz"})
    assert history_db.summary() == "Pretty: XYZ"


def test_load_handles_corrupt_file(tmp_path, capsys):
    file_path = tmp_path / "corrupt.json"
    file_path.write_text("not json")
    db = HistoryDB(
        file_path=file_path,
        empty={"foo": "empty"},
    )
    # forcibly break the file
    result = db.latest()
    assert result == {"foo": "empty"}
    captured = capsys.readouterr()
    assert "Failed to load" in captured.err


def test_save_handles_write_exception(tmp_path, capsys, monkeypatch):
    file_path = tmp_path / "fail.json"
    file_path.write_text(json.dumps([{"foo": "empty"}]))
    db = HistoryDB(
        file_path=file_path,
        empty={"foo": "empty"},
    )

    def raise_exc(*a, **kw):
        raise IOError("disk full")

    monkeypatch.setattr("builtins.open", lambda *a, **kw: raise_exc())
    db._save([{"foo": "fail"}])
    captured = capsys.readouterr()
    assert "Failed to save" in captured.err
