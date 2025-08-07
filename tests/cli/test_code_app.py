import pytest
import typer
from unittest.mock import patch, MagicMock, call
from typer.testing import CliRunner

from crowler.cli.code_app import code_app, create_unit_test


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_ai_client():
    with patch("crowler.cli.code_app.get_ai_client") as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_get_processing_files():
    with patch("crowler.cli.code_app.get_processing_files") as mock:
        mock.return_value = ["file1.py", "file2.py"]
        yield mock


@pytest.fixture
def mock_rewrite_files():
    with patch("crowler.cli.code_app.rewrite_files") as mock:
        yield mock


@pytest.fixture
def mock_parse_code_response():
    with patch("crowler.cli.code_app.parse_code_response") as mock:
        mock.return_value = {"test_file.py": "test content"}
        yield mock


def test_create_unit_tests_command(
    runner,
    mock_ai_client,
    mock_get_processing_files,
    mock_rewrite_files,
    mock_parse_code_response,
):
    # Setup
    mock_ai_client.send_message.return_value = "test response"

    # Call the command
    result = runner.invoke(code_app, ["unit-test", "--force"])

    # Assertions
    assert result.exit_code == 0
    assert mock_ai_client.send_message.call_count == 2  # Once for each file
    mock_parse_code_response.assert_has_calls(
        [call("test response"), call("test response")]
    )
    assert mock_rewrite_files.call_count == 2


def test_create_unit_test_function(
    mock_ai_client, mock_rewrite_files, mock_parse_code_response
):
    # Setup
    mock_ai_client.send_message.return_value = "test response"

    # Call the function
    create_unit_test(True, "test_file.py")

    # Assertions
    mock_ai_client.send_message.assert_called_once()
    mock_parse_code_response.assert_called_once_with("test response")
    mock_rewrite_files.assert_called_once_with(
        files={"test_file.py": "test content"}, force=True
    )


def test_create_unit_test_function_skips_init_files(mock_ai_client, mock_rewrite_files):
    # Setup
    with patch("typer.secho") as mock_secho:
        # Call the function
        create_unit_test(True, "__init__.py")

        # Assertions
        mock_ai_client.send_message.assert_not_called()
        mock_rewrite_files.assert_not_called()
        mock_secho.assert_called_once()
        assert "__init__.py" in mock_secho.call_args[0][0]


def test_create_readme_command(
    runner, mock_ai_client, mock_rewrite_files, mock_parse_code_response
):
    # Setup
    mock_ai_client.send_message.return_value = "readme response"

    # Call the command
    result = runner.invoke(code_app, ["readme", "--force"])

    # Assertions
    assert result.exit_code == 0
    mock_ai_client.send_message.assert_called_once()
    mock_parse_code_response.assert_called_once_with("readme response")
    mock_rewrite_files.assert_called_once_with(
        files={"test_file.py": "test content"}, force=True
    )


def test_create_readme_command_handles_exception(runner, mock_ai_client):
    # Setup
    mock_ai_client.send_message.side_effect = Exception("Test error")

    with patch("typer.secho") as mock_secho:
        # Call the command
        result = runner.invoke(code_app, ["readme", "--force"])

        # Assertions
        assert result.exit_code == 0  # Should not raise exception to typer
        mock_secho.assert_called_once()
        assert "Failed to create README.md" in mock_secho.call_args[0][0]


def test_fix_mypy_errors_command(
    runner,
    mock_ai_client,
    mock_get_processing_files,
    mock_rewrite_files,
    mock_parse_code_response,
):
    # Setup
    mock_ai_client.send_message.return_value = "mypy response"

    # Call the command
    result = runner.invoke(code_app, ["mypy", "--force"])

    # Assertions
    assert result.exit_code == 0
    assert mock_ai_client.send_message.call_count == 2  # Once for each file
    mock_parse_code_response.assert_has_calls(
        [call("mypy response"), call("mypy response")]
    )
    assert mock_rewrite_files.call_count == 2


def test_fix_mypy_errors_command_handles_exception(
    runner, mock_ai_client, mock_get_processing_files
):
    # Setup
    mock_ai_client.send_message.side_effect = Exception("Test error")

    with patch("typer.secho") as mock_secho:
        # Call the command
        result = runner.invoke(code_app, ["mypy", "--force"])

        # Assertions
        assert result.exit_code == 0  # Should not raise exception to typer
        assert mock_secho.call_count == 2  # Once for each file
        assert "Failed to fix mypy errors" in mock_secho.call_args_list[0][0][0]


def test_improve_typer_logs_command(
    runner,
    mock_ai_client,
    mock_get_processing_files,
    mock_rewrite_files,
    mock_parse_code_response,
):
    # Setup
    mock_ai_client.send_message.return_value = "typer log response"

    # Call the command
    result = runner.invoke(code_app, ["typer-log", "--force"])

    # Assertions
    assert result.exit_code == 0
    assert mock_ai_client.send_message.call_count == 2  # Once for each file
    mock_parse_code_response.assert_has_calls(
        [call("typer log response"), call("typer log response")]
    )
    assert mock_rewrite_files.call_count == 2


def test_improve_typer_logs_command_skips_init_files(
    runner, mock_ai_client, mock_get_processing_files
):
    # Setup
    mock_get_processing_files.return_value = ["file1.py", "__init__.py"]

    with patch("typer.secho") as mock_secho:
        # Call the command
        result = runner.invoke(code_app, ["typer-log", "--force"])

        # Assertions
        assert result.exit_code == 0
        assert (
            mock_ai_client.send_message.call_count == 1
        )  # Only once for non-init file
        assert mock_secho.call_count >= 1
        assert "__init__.py" in mock_secho.call_args_list[0][0][0]


def test_improve_typer_logs_command_handles_exception(
    runner, mock_ai_client, mock_get_processing_files
):
    # Setup
    mock_ai_client.send_message.side_effect = Exception("Test error")

    with patch("typer.secho") as mock_secho:
        # Call the command
        result = runner.invoke(code_app, ["typer-log", "--force"])

        # Assertions
        assert result.exit_code == 0  # Should not raise exception to typer
        assert mock_secho.call_count == 2  # Once for each file
        assert "Failed to improve typer logs" in mock_secho.call_args_list[0][0][0]
