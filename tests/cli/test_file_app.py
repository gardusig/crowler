import pytest
from typer.testing import CliRunner
from crowler.cli.file_app import file_app
from unittest.mock import patch, MagicMock

runner = CliRunner()


@pytest.fixture
def mock_dependencies():
    # The app_factory imports get_all_files, so we need to patch it there
    with (
        patch("crowler.cli.app_factory.get_all_files") as mock_get_all_files,
        patch("crowler.db.shared_file_db.append_shared_file") as mock_append,
        patch("crowler.db.shared_file_db.remove_shared_file") as mock_remove,
        patch("crowler.db.shared_file_db.clear_shared_files") as mock_clear,
        patch(
            "crowler.db.shared_file_db.summary_shared_files",
            return_value="📁 Shared files:\n- /path/to/file1\n- /path/to/file2",
        ) as mock_summary,
        patch("crowler.db.shared_file_db.undo_shared_files") as mock_undo,
    ):
        # Set up get_all_files to return our test files
        mock_get_all_files.return_value = ["/path/to/file1", "/path/to/file2"]

        yield {
            "get_all_files": mock_get_all_files,
            "append": mock_append,
            "remove": mock_remove,
            "clear": mock_clear,
            "summary": mock_summary,
            "undo": mock_undo,
        }


def test_add_file(mock_dependencies):
    result = runner.invoke(file_app, ["add", "/path/to"])
    assert result.exit_code == 0

    # Verify get_all_files was called with the correct path
    mock_dependencies["get_all_files"].assert_called_once_with("/path/to")

    # Verify append was called for each file
    mock_dependencies["append"].assert_any_call("/path/to/file1")
    mock_dependencies["append"].assert_any_call("/path/to/file2")
    assert mock_dependencies["append"].call_count == 2


def test_remove_file(mock_dependencies):
    # For remove operations with should_handle_filepaths=True, it also uses get_all_files
    result = runner.invoke(file_app, ["remove", "/path/to/file1"])
    assert result.exit_code == 0

    # Verify get_all_files was called
    mock_dependencies["get_all_files"].assert_called_once_with("/path/to/file1")

    # Verify remove was called with the returned file
    mock_dependencies["remove"].assert_called_once_with("/path/to/file1")


def test_clear_files(mock_dependencies):
    result = runner.invoke(file_app, ["clear"])
    assert result.exit_code == 0
    mock_dependencies["clear"].assert_called_once()


def test_list_files(mock_dependencies):
    result = runner.invoke(file_app, ["list"])
    assert result.exit_code == 0
    mock_dependencies["summary"].assert_called_once()
    assert "/path/to/file1" in result.output
    assert "/path/to/file2" in result.output


def test_undo_file(mock_dependencies):
    result = runner.invoke(file_app, ["undo"])
    assert result.exit_code == 0
    mock_dependencies["undo"].assert_called_once()
