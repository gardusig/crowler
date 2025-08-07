
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

runner = CliRunner()


@patch('crowler.db.shared_file_db.get_shared_files')
@patch('crowler.db.shared_file_db.append_shared_file')
@patch('crowler.util.file_util.get_all_files')
def test_add_file(mock_get_all_files, mock_append_shared_file, mock_get_shared_files):
    """Test the add command"""
    # Import inside the test to ensure patches are applied before app is loaded
    from crowler.cli.file_app import file_app
    
    # Setup mock return values
    mock_get_all_files.return_value = ["/path/to/file1", "/path/to/file2"]
    
    # Run the command
    result = runner.invoke(file_app, ["add", "/path/to"])
    
    # Verify command execution and output
    assert result.exit_code == 0
    mock_get_all_files.assert_called_once_with("/path/to")
    mock_append_shared_file.assert_has_calls([
        call("/path/to/file1"),
        call("/path/to/file2")
    ])


@patch('crowler.db.shared_file_db.get_shared_files')
@patch('crowler.db.shared_file_db.remove_shared_file')
@patch('crowler.util.file_util.get_all_files')
def test_remove_file(mock_get_all_files, mock_remove_shared_file, mock_get_shared_files):
    """Test the remove command"""
    # Import inside the test to ensure patches are applied before app is loaded
    from crowler.cli.file_app import file_app
    
    # Setup mock return values
    mock_get_all_files.return_value = ["/path/to/file1", "/path/to/file2"]
    
    # Run the command
    result = runner.invoke(file_app, ["remove", "/path/to/file1"])
    
    # Verify command execution and output
    assert result.exit_code == 0
    mock_get_all_files.assert_called_once_with("/path/to/file1")
    mock_remove_shared_file.assert_has_calls([
        call("/path/to/file1"),
        call("/path/to/file2")
    ])


@patch('crowler.db.shared_file_db.clear_shared_files')
def test_clear_files(mock_clear_shared_files):
    """Test the clear command"""
    # Import inside the test to ensure patches are applied before app is loaded
    from crowler.cli.file_app import file_app
    
    # Run the command
    result = runner.invoke(file_app, ["clear"])
    
    # Verify command execution and output
    assert result.exit_code == 0
    mock_clear_shared_files.assert_called_once()


@patch('crowler.db.shared_file_db.summary_shared_files')
def test_list_files(mock_summary_shared_files):
    """Test the list command"""
    # Import inside the test to ensure patches are applied before app is loaded
    from crowler.cli.file_app import file_app
    
    # Setup mock return values
    expected_summary = "📁 Shared files:\n- /path/to/file1\n- /path/to/file2"
    mock_summary_shared_files.return_value = expected_summary
    
    # Run the command
    result = runner.invoke(file_app, ["list"])
    
    # Verify command execution and output
    assert result.exit_code == 0
    mock_summary_shared_files.assert_called_once()
    assert expected_summary in result.stdout


@patch('crowler.db.shared_file_db.undo_shared_files')
def test_undo_file(mock_undo_shared_files):
    """Test the undo command"""
    # Import inside the test to ensure patches are applied before app is loaded
    from crowler.cli.file_app import file_app
    
    # Run the command
    result = runner.invoke(file_app, ["undo"])
    
    # Verify command execution and output
    assert result.exit_code == 0
    mock_undo_shared_files.assert_called_once()
