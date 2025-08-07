import pytest
from unittest.mock import patch

from crowler.ai.aws.anthropic.claude_client import ClaudeClient


class DummyConfig:
    anthropic_version = "2023-06-01"
    model = "claude-3-haiku"
    max_tokens = 1024
    temperature = 0.5
    top_p = 0.9
    reasoning_max_tokens = None  # Adding this required attribute


@pytest.fixture
def dummy_config():
    return DummyConfig()


def test_format_request_body_returns_correct_dict(monkeypatch, dummy_config):
    client = ClaudeClient(config=dummy_config)
    # Patch the config to avoid cast issues
    monkeypatch.setattr(client, "config", dummy_config)
    messages = [{"role": "user", "content": "Hello"}]
    result = client._format_request_body(messages)
    assert result["anthropic_version"] == dummy_config.anthropic_version
    assert result["max_tokens"] == dummy_config.max_tokens
    assert result["temperature"] == dummy_config.temperature
    assert result["top_p"] == dummy_config.top_p
    assert result["messages"] == messages


def test_parse_response_extracts_text():
    client = ClaudeClient(config=DummyConfig())
    # Fixed: Adding the "type" field that the parser expects
    raw = {"content": [{"type": "text", "text": "Hello, world!"}]}

    # Mock typer.secho to avoid console output during tests
    with patch("crowler.ai.aws.anthropic.claude_client.typer.secho"):
        result = client._parse_response(raw)

    assert result == "Hello, world!"


def test_init_uses_default_config(monkeypatch):
    # Patch Claude37ClientConfig to a dummy config to check default usage
    from crowler.ai.aws.anthropic import claude_client as cc_mod

    class DummyDefaultConfig(DummyConfig):
        pass

    monkeypatch.setattr(cc_mod, "Claude37ClientConfig", lambda: DummyDefaultConfig())
    client = ClaudeClient()
    assert isinstance(client.config, DummyDefaultConfig)
