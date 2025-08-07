import pytest
import typer
from unittest.mock import patch, MagicMock, call, ANY  # Import ANY from unittest.mock
from typer.testing import CliRunner
from collections import OrderedDict

from crowler.cli.code_app import code_app, create_unit_test
from crowler.util.string_util import TaskType


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
        # Return file paths that will match our test files
        mock.return_value = OrderedDict(
            [("file1.py", "test content"), ("file2.py", "test content")]
        )
        yield mock


@pytest.fixture
def mock_readme_parser():
    with patch("crowler.cli.code_app.parse_code_response") as mock:
        # For README tests, return appropriate README content
        mock.return_value = OrderedDict(
            [("README.md", "# Project Title\n\nProject description")]
        )
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
    mock_ai_client.send_message.assert_has_calls(
        [
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # UNIT_TEST_INSTRUCTION
                ],
                prompt_files=["file1.py"],
                final_prompt='Focus only on creating|fixing test(s) for "file1.py"',
            ),
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # UNIT_TEST_INSTRUCTION
                ],
                prompt_files=["file2.py"],
                final_prompt='Focus only on creating|fixing test(s) for "file2.py"',
            ),
        ]
    )
    mock_parse_code_response.assert_has_calls(
        [
            call(response="test response", task_type=TaskType.TEST_GENERATION),
            call(response="test response", task_type=TaskType.TEST_GENERATION),
        ]
    )
    assert mock_rewrite_files.call_count == 2


def test_create_unit_test_function(
    mock_ai_client, mock_rewrite_files, mock_parse_code_response
):
    # Setup
    mock_ai_client.send_message.return_value = "test response"
    # The key needs to match the filepath for the function's if condition to pass
    mock_parse_code_response.return_value = OrderedDict(
        [("test_file.py", "test content")]
    )

    # Call the function
    create_unit_test(True, "test_file.py")

    # Assertions
    mock_ai_client.send_message.assert_called_once_with(
        instructions=[
            ANY,  # RESPONSE_FORMAT_INSTRUCTION
            ANY,  # UNIT_TEST_INSTRUCTION
        ],
        prompt_files=["test_file.py"],
        final_prompt='Focus only on creating|fixing test(s) for "test_file.py"',
    )
    mock_parse_code_response.assert_called_once_with(
        response="test response", task_type=TaskType.TEST_GENERATION
    )
    mock_rewrite_files.assert_called_once_with(
        files=OrderedDict([("test_file.py", "test content")]), force=True
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
        assert "Skipping" in mock_secho.call_args[0][0]


def test_create_readme_command(
    runner, mock_ai_client, mock_rewrite_files, mock_readme_parser
):
    # Setup
    mock_ai_client.send_message.return_value = "readme response"

    # Call the command
    result = runner.invoke(code_app, ["readme", "--force"])

    # Assertions
    assert result.exit_code == 0
    mock_ai_client.send_message.assert_called_once_with(
        instructions=[
            ANY,  # RESPONSE_FORMAT_INSTRUCTION
            ANY,  # README_INSTRUCTION
        ],
        prompt_files=["./README.md"],
        final_prompt='Focus only on creating a single "README.md"',
    )
    mock_readme_parser.assert_called_once_with("readme response")
    mock_rewrite_files.assert_called_once_with(
        files=OrderedDict([("README.md", "# Project Title\n\nProject description")]),
        force=True,
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
        assert "Test error" in mock_secho.call_args[0][0]


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
    mock_ai_client.send_message.assert_has_calls(
        [
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # MYPY_INSTRUCTION
                ],
                prompt_files=["file1.py"],
                final_prompt="Focus on fixing only mypy errors related to file1.py",
            ),
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # MYPY_INSTRUCTION
                ],
                prompt_files=["file2.py"],
                final_prompt="Focus on fixing only mypy errors related to file2.py",
            ),
        ]
    )
    mock_parse_code_response.assert_has_calls(
        [call("mypy response"), call("mypy response")]
    )
    mock_rewrite_files.assert_has_calls(
        [
            call(
                files=OrderedDict(
                    [("file1.py", "test content"), ("file2.py", "test content")]
                ),
                force=True,
            ),
            call(
                files=OrderedDict(
                    [("file1.py", "test content"), ("file2.py", "test content")]
                ),
                force=True,
            ),
        ]
    )


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
        assert "Test error" in mock_secho.call_args_list[0][0][0]


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
    mock_ai_client.send_message.assert_has_calls(
        [
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # TYPER_LOG_INSTRUCTION
                ],
                prompt_files=["file1.py"],
                final_prompt="Focus on only file1.py",
            ),
            call(
                instructions=[
                    ANY,  # RESPONSE_FORMAT_INSTRUCTION
                    ANY,  # TYPER_LOG_INSTRUCTION
                ],
                prompt_files=["file2.py"],
                final_prompt="Focus on only file2.py",
            ),
        ]
    )
    mock_parse_code_response.assert_has_calls(
        [call("typer log response"), call("typer log response")]
    )
    mock_rewrite_files.assert_has_calls(
        [
            call(
                files=OrderedDict(
                    [("file1.py", "test content"), ("file2.py", "test content")]
                ),
                force=True,
            ),
            call(
                files=OrderedDict(
                    [("file1.py", "test content"), ("file2.py", "test content")]
                ),
                force=True,
            ),
        ]
    )


def test_improve_typer_logs_command_skips_init_files(
    runner, mock_ai_client, mock_rewrite_files
):
    # Setup - use a more explicit list of files with an __init__.py
    with patch("crowler.cli.code_app.get_processing_files") as mock_get_files:
        mock_get_files.return_value = ["file1.py", "__init__.py"]

        with patch("typer.secho") as mock_secho:
            with patch("crowler.cli.code_app.parse_code_response") as mock_parse:
                mock_parse.return_value = OrderedDict([("file1.py", "test content")])
                mock_ai_client.send_message.return_value = "typer log response"

                # Call the command
                result = runner.invoke(code_app, ["typer-log", "--force"])

                # Assertions
                assert result.exit_code == 0

                # Should only call send_message for file1.py, not for __init__.py
                mock_ai_client.send_message.assert_called_once_with(
                    instructions=[
                        ANY,  # RESPONSE_FORMAT_INSTRUCTION
                        ANY,  # TYPER_LOG_INSTRUCTION
                    ],
                    prompt_files=["file1.py"],
                    final_prompt="Focus on only file1.py",
                )

                # Should only call rewrite_files once
                mock_rewrite_files.assert_called_once_with(
                    files=OrderedDict([("file1.py", "test content")]), force=True
                )

                # Should print a message about skipping __init__.py
                skip_message_calls = [
                    args
                    for args, _ in mock_secho.call_args_list
                    if "__init__.py" in args[0] and "Skipping" in args[0]
                ]
                assert len(skip_message_calls) == 1


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
        assert "Test error" in mock_secho.call_args_list[0][0][0]
