import pytest
from unittest.mock import patch, MagicMock, call
from typer.testing import CliRunner

runner = CliRunner()

# Import the app here since we'll patch functions directly in each test
from crowler.cli.process_app import process_app


def test_add_file():
    """Test the add command for processing files."""
    with (
        patch(
            "crowler.cli.app_factory.get_all_files",
            return_value=["file1.txt", "file2.txt"],
        ) as mock_get_files,
        patch("crowler.db.process_file_db.append_processing_file") as mock_append,
    ):

        result = runner.invoke(process_app, ["add", "dummy_path"])

        assert result.exit_code == 0
        mock_get_files.assert_called_once_with("dummy_path")

        assert mock_append.call_count == 2
        mock_append.assert_has_calls(
            [call("file1.txt"), call("file2.txt")], any_order=True
        )


def test_remove_file():
    """Test the remove command for processing files."""
    with (
        patch(
            "crowler.cli.app_factory.get_all_files",
            return_value=["file1.txt", "file2.txt"],
        ) as mock_get_files,
        patch("crowler.db.process_file_db.remove_processing_file") as mock_remove,
    ):

        result = runner.invoke(process_app, ["remove", "dummy_path"])

        assert result.exit_code == 0
        mock_get_files.assert_called_once_with("dummy_path")

        assert mock_remove.call_count == 2
        mock_remove.assert_has_calls(
            [call("file1.txt"), call("file2.txt")], any_order=True
        )


def test_clear_files():
    """Test the clear command for processing files."""
    with patch("crowler.db.process_file_db.clear_processing_files") as mock_clear:
        result = runner.invoke(process_app, ["clear"])

        assert result.exit_code == 0
        mock_clear.assert_called_once()


def test_list_files():
    """Test the list command for processing files."""
    expected_output = "🔄 Processing files:\n- file1.txt\n- file2.txt"
    with patch(
        "crowler.db.process_file_db.summary_processing_files",
        return_value=expected_output,
    ) as mock_summary:
        result = runner.invoke(process_app, ["list"])

        assert result.exit_code == 0
        mock_summary.assert_called_once()
        assert expected_output in result.output


def test_undo_file():
    """Test the undo command for processing files."""
    with patch("crowler.db.process_file_db.undo_processing_files") as mock_undo:
        result = runner.invoke(process_app, ["undo"])

        assert result.exit_code == 0
        mock_undo.assert_called_once()
