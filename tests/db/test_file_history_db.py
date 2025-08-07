import pytest
from unittest.mock import patch, MagicMock
import typer

# Patch external dependencies at the top of the module
patch("crowler.db.file_history_db.HistoryDB", autospec=True).start()
patch(
    "crowler.db.file_history_db.create_session_file",
    return_value="mocked_session_file",
).start()

from crowler.db.file_history_db import FileHistoryStore


@pytest.fixture(autouse=True)
def cleanup_patches():
    # Cleanup all patches after each test
    yield
    patch.stopall()


@pytest.fixture
def mock_historydb(monkeypatch):
    # Patch HistoryDB instance methods for each test
    mock_db = MagicMock()
    monkeypatch.setattr(
        "crowler.db.file_history_db.HistoryDB", lambda *a, **kw: mock_db
    )
    return mock_db


@pytest.fixture
def store(mock_historydb):
    return FileHistoryStore("test_name", "Test Label")


def test_append_adds_new_path(store, mock_historydb):
    # Remove capsys as we don't expect output from FileHistoryStore directly
    mock_historydb.latest.return_value = []
    store.append("  /foo/bar.txt  ")
    assert mock_historydb.push.called
    args, kwargs = mock_historydb.push.call_args
    assert "/foo/bar.txt" in args[0]
    # FileHistoryStore doesn't print success messages


@pytest.mark.parametrize("input_path", ["", "   "])
def test_append_empty_path(store, mock_historydb, capsys, input_path):
    store.append(input_path)
    assert not mock_historydb.push.called
    captured = capsys.readouterr()
    assert "⚠️  Empty path" in captured.out


def test_append_duplicate_path(store, mock_historydb, capsys):
    mock_historydb.latest.return_value = ["foo.txt"]
    store.append("foo.txt")
    assert not mock_historydb.push.called
    captured = capsys.readouterr()
    assert "⚠️  Path already present: foo.txt" in captured.out


def test_remove_existing_path(store, mock_historydb):
    # Remove capsys as we don't expect output from FileHistoryStore directly
    mock_historydb.latest.return_value = ["foo.txt", "bar.txt"]
    store.remove("foo.txt")
    assert mock_historydb.push.called
    args, kwargs = mock_historydb.push.call_args
    assert "foo.txt" not in args[0]
    # FileHistoryStore doesn't print success messages


def test_remove_empty_path(store, mock_historydb, capsys):
    store.remove("   ")
    assert not mock_historydb.push.called
    captured = capsys.readouterr()
    assert "⚠️  Empty path" in captured.out


def test_remove_nonexistent_path(store, mock_historydb, capsys):
    mock_historydb.latest.return_value = ["foo.txt"]
    store.remove("bar.txt")
    assert not mock_historydb.push.called
    captured = capsys.readouterr()
    assert "⚠️  Path not tracked: bar.txt" in captured.out


def test_clear_calls_db_clear(store, mock_historydb):
    # Renamed test and removed capsys as we don't expect output
    store.clear()
    assert mock_historydb.clear.called
    # FileHistoryStore doesn't print success messages


def test_undo_success(store, mock_historydb, capsys):
    mock_historydb.undo.return_value = True
    store.undo()
    captured = capsys.readouterr()
    assert "↩️ Reverted last change." in captured.out


def test_undo_failure(store, mock_historydb, capsys):
    mock_historydb.undo.return_value = False
    store.undo()
    captured = capsys.readouterr()
    assert "⚠️  Nothing to undo." in captured.out


def test_summary_returns_db_summary(store, mock_historydb):
    mock_historydb.summary.return_value = "summary text"
    assert store.summary() == "summary text"


def test_latest_set_returns_set(store, mock_historydb):
    mock_historydb.latest.return_value = ["a.txt", "b.txt"]
    result = store.latest_set()
    assert result == {"a.txt", "b.txt"}
