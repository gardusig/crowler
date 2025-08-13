import pyperclip
from typer.testing import CliRunner
from unittest.mock import patch
from crowler.cli.app import app

runner = CliRunner()


def test_preview_command():
    with (
        patch(
            "crowler.cli.app.summary_prompts", return_value="Prompt Summary"
        ) as mock_summary_prompts,
        patch(
            "crowler.cli.app.summary_shared_files",
            return_value="Shared Files Summary",
        ) as mock_summary_shared_files,
        patch(
            "crowler.cli.app.summary_processing_files",
            return_value="Processing Files Summary",
        ) as mock_summary_processing_files,
        patch(
            "crowler.cli.app.summary_urls",
            return_value="URLs Summary",
        ) as mock_summary_urls,
    ):

        result = runner.invoke(app, ["show"])

        assert result.exit_code == 0
        assert "Prompt Summary" in result.output
        assert "Shared Files Summary" in result.output
        assert "Processing Files Summary" in result.output
        assert "URLs Summary" in result.output

        mock_summary_prompts.assert_called_once()
        mock_summary_shared_files.assert_called_once()
        mock_summary_processing_files.assert_called_once()
        mock_summary_urls.assert_called_once()


def test_clear_all_command():
    with (
        patch("crowler.cli.app.clear_prompts") as mock_clear_prompts,
        patch("crowler.cli.app.clear_shared_files") as mock_clear_shared_files,
        patch("crowler.cli.app.clear_processing_files") as mock_clear_processing_files,
        patch("crowler.cli.app.clear_urls") as mock_clear_urls,
    ):

        result = runner.invoke(app, ["clear"])

        assert result.exit_code == 0
        mock_clear_prompts.assert_called_once()
        mock_clear_shared_files.assert_called_once()
        mock_clear_processing_files.assert_called_once()
        mock_clear_urls.assert_called_once()


def test_add_prompt_from_clipboard():
    # Mock both clipboard function and DB function for proper isolation
    with (
        patch(
            "crowler.cli.app._clipboard_get", return_value="Clipboard prompt"
        ) as mock_clipboard_get,
        patch("crowler.cli.app.append_prompt") as mock_append_prompt,
    ):

        result = runner.invoke(app, ["paste"])

        assert result.exit_code == 0
        mock_clipboard_get.assert_called_once()
        mock_append_prompt.assert_called_once_with("Clipboard prompt")


def test_clipboard_get_unavailable():
    with patch("pyperclip.paste", side_effect=pyperclip.PyperclipException):
        # The command is 'paste' not 'clipboard'
        result = runner.invoke(app, ["paste"])
        assert result.exit_code == 1


def test_copy_to_clipboard():
    # Test the copy command
    with (
        patch(
            "crowler.cli.app.summary_all", return_value="All summaries"
        ) as mock_summary_all,
        patch("crowler.cli.app._clipboard_set") as mock_clipboard_set,
    ):

        result = runner.invoke(app, ["copy"])

        assert result.exit_code == 0
        mock_summary_all.assert_called_once()
        mock_clipboard_set.assert_called_once_with("All summaries")


def test_ask_command():
    # Test the ask command with mocked environment variable
    with (
        patch("os.environ", {"AI_CLIENT": "openai"}),
        patch("crowler.cli.app.get_ai_client") as mock_get_client,
    ):
        mock_client = mock_get_client.return_value
        mock_client.send_message.return_value = "AI response"

        result = runner.invoke(app, ["ask"])

        assert result.exit_code == 0
        mock_get_client.assert_called_once()
        mock_client.send_message.assert_called_once()
        assert "AI response" in result.stdout
