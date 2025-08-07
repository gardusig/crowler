import pytest
from typer.testing import CliRunner
from crowler.cli.process_app import process_app
from unittest.mock import patch, call

runner = CliRunner()


@pytest.fixture
def mock_file_operations():
    # Patch functions at their actual import locations
    with (
        # get_all_files is imported in app_factory, not directly in process_app
        patch("crowler.cli.app_factory.get_all_files") as mock_get_all_files,
        # These are the actual DB functions that get called
        patch("crowler.db.process_file_db.append_processing_file") as mock_append,
        patch("crowler.db.process_file_db.remove_processing_file") as mock_remove,
        patch("crowler.db.process_file_db.clear_processing_files") as mock_clear,
        patch("crowler.db.process_file_db.summary_processing_files") as mock_summary,
        patch("crowler.db.process_file_db.undo_processing_files") as mock_undo,
    ):
        mock_get_all_files.return_value = ["file1.txt", "file2.txt"]
        mock_summary.return_value = "Current files: file1.txt, file2.txt"
        yield {
            "get_all_files": mock_get_all_files,
            "append": mock_append,
            "remove": mock_remove,
            "clear": mock_clear,
            "summary": mock_summary,
            "undo": mock_undo,
        }


def test_add_file(mock_file_operations):
    result = runner.invoke(process_app, ["add", "dummy_path"])
    assert result.exit_code == 0
    mock_file_operations["get_all_files"].assert_called_once_with("dummy_path")
    mock_file_operations["append"].assert_has_calls(
        [call("file1.txt"), call("file2.txt")]
    )


def test_remove_file(mock_file_operations):
    result = runner.invoke(process_app, ["remove", "path"])
    assert result.exit_code == 0
    mock_file_operations["get_all_files"].assert_called_once_with("path")
    mock_file_operations["remove"].assert_has_calls(
        [call("file1.txt"), call("file2.txt")]
    )


def test_clear_files(mock_file_operations):
    result = runner.invoke(process_app, ["clear"])
    assert result.exit_code == 0
    mock_file_operations["clear"].assert_called_once()


def test_list_files(mock_file_operations):
    result = runner.invoke(process_app, ["list"])
    assert result.exit_code == 0
    assert "Current files: file1.txt, file2.txt" in result.output
    mock_file_operations["summary"].assert_called_once()


def test_undo_file(mock_file_operations):
    result = runner.invoke(process_app, ["undo"])
    assert result.exit_code == 0
    mock_file_operations["undo"].assert_called_once()
