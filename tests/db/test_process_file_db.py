import pytest
from unittest.mock import patch, MagicMock

import crowler.db.process_file_db as process_file_db


@pytest.fixture(autouse=True)
def patch_file_history_store(monkeypatch):
    # Patch FileHistoryStore in the process_file_db module
    mock_store = MagicMock()
    monkeypatch.setattr(process_file_db, "_proc_store", mock_store)
    return mock_store


@pytest.fixture
def mock_typer_secho():
    with patch("crowler.db.process_file_db.typer.secho") as mock_secho:
        yield mock_secho


def test_clear_processing_files_calls_clear(patch_file_history_store, mock_typer_secho):
    process_file_db.clear_processing_files()
    patch_file_history_store.clear.assert_called_once_with()
    mock_typer_secho.assert_called_once_with("✅ Processing files cleared.", fg="green")


def test_append_processing_file_calls_append(
    patch_file_history_store, mock_typer_secho
):
    process_file_db.append_processing_file("foo.txt")
    patch_file_history_store.append.assert_called_once_with("foo.txt")
    mock_typer_secho.assert_called_once_with(
        "✅ Processing file appended: foo.txt", fg="green"
    )


def test_remove_processing_file_calls_remove(
    patch_file_history_store, mock_typer_secho
):
    process_file_db.remove_processing_file("bar.txt")
    patch_file_history_store.remove.assert_called_once_with("bar.txt")
    mock_typer_secho.assert_called_once_with(
        "✅ Processing file removed: bar.txt", fg="green"
    )


def test_undo_processing_files_calls_undo(patch_file_history_store, mock_typer_secho):
    process_file_db.undo_processing_files()
    patch_file_history_store.undo.assert_called_once_with()
    mock_typer_secho.assert_called_once_with(
        "✅ Undo completed for processing files.", fg="green"
    )


def test_summary_processing_files_returns_summary(patch_file_history_store):
    patch_file_history_store.summary.return_value = "summary!"
    result = process_file_db.summary_processing_files()
    patch_file_history_store.summary.assert_called_once_with()
    assert result == "summary!"


def test_get_processing_files_returns_latest_set(patch_file_history_store):
    patch_file_history_store.latest_set.return_value = {"a.txt", "b.txt"}
    result = process_file_db.get_processing_files()
    patch_file_history_store.latest_set.assert_called_once_with()
    assert result == {"a.txt", "b.txt"}
