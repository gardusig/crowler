# tests/cli/test_url_app.py
from unittest.mock import patch, call, Mock
import pytest
from typer.testing import CliRunner

runner = CliRunner()


def test_parse_urls_success():
    # Patch get_urls and extract_html_data where parse_urls looks them up
    with (
        patch("crowler.cli.url_app.get_urls") as mock_get_urls,
        patch("crowler.cli.url_app.extract_html_data") as mock_extract,
    ):

        # Arrange: two example URLs and mocked extracted data
        mock_get_urls.return_value = ["https://a.example", "https://b.example"]
        mock_extract.side_effect = ["DATA A", "DATA B"]

        # Import the Typer app and run the 'parse' command
        from crowler.cli.url_app import url_app

        result = runner.invoke(url_app, ["parse"])

        # Assert exit code and calls
        assert result.exit_code == 0
        mock_get_urls.assert_called_once()
        mock_extract.assert_has_calls(
            [call("https://a.example"), call("https://b.example")]
        )

        # Click/Typer's CliRunner returns combined stdout+stderr in result.output.
        # We expect the printed data to appear in output.
        assert "DATA A" in result.output
        assert "DATA B" in result.output


def test_parse_urls_failure():
    # Simulate extract_html_data raising for the first URL
    with (
        patch("crowler.cli.url_app.get_urls") as mock_get_urls,
        patch("crowler.cli.url_app.extract_html_data") as mock_extract,
    ):

        mock_get_urls.return_value = ["https://bad.example"]
        # Make extract_html_data raise
        mock_extract.side_effect = RuntimeError("boom")

        from crowler.cli.url_app import url_app

        result = runner.invoke(url_app, ["parse"])

        # Because parse_urls catches, secho's an error and then re-raises,
        # the command should exit with non-zero code.
        assert result.exit_code != 0

        # The secho error message should appear in the output (stderr merged into result.output)
        assert (
            "❌ Failed to undo last change" in result.output
            or "Failed to undo" in result.output
        )
        # Optional: assert the exception message is in output or raised in exception
        assert (
            "boom" in result.output
            or "RuntimeError" in result.stdout
            or "boom" in str(result.exception)
        )
