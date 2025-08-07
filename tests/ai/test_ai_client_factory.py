from typing import Optional
import pytest
import types

import crowler.ai.ai_client_factory as ai_client_factory


# Mock implementation of AIConfig for testing
class MockAIConfig:
    def __init__(self):
        self.model = "test-model"
        self.temperature = 0.7
        self.top_p = 0.9
        self.max_tokens = 1024


@pytest.fixture(autouse=True)
def patch_ai_clients(monkeypatch):
    def dummy_openai(config=None):
        return types.SimpleNamespace(name="openai", config=config)

    def dummy_claude(config=None):
        return types.SimpleNamespace(name="claude", config=config)

    monkeypatch.setitem(ai_client_factory.AI_CLIENTS, "openai", dummy_openai)
    monkeypatch.setitem(ai_client_factory.AI_CLIENTS, "claude", dummy_claude)
    yield


@pytest.mark.parametrize(
    "env_value,expected_name",
    [
        ("openai", "openai"),
        ("claude", "claude"),
        ("OPENAI", "openai"),
        ("  claude  ", "claude"),
    ],
)
def test_get_ai_client_valid(monkeypatch, env_value, expected_name):
    monkeypatch.setenv("AI_CLIENT", env_value)
    config = MockAIConfig()  # Use mock implementation instead of protocol
    client = ai_client_factory.get_ai_client(config)
    assert client.name == expected_name
    assert client.config is config


def test_get_ai_client_env_not_set(monkeypatch):
    monkeypatch.delenv("AI_CLIENT", raising=False)
    with pytest.raises(RuntimeError) as excinfo:
        ai_client_factory.get_ai_client()
    assert "AI_CLIENT environment variable not set" in str(excinfo.value)


def test_get_ai_client_unsupported_client(monkeypatch):
    monkeypatch.setenv("AI_CLIENT", "unknown_client")
    with pytest.raises(ValueError) as excinfo:
        ai_client_factory.get_ai_client()
    assert "Unsupported AI_CLIENT" in str(excinfo.value)
    assert "unknown_client" in str(excinfo.value)
    assert "openai" in str(excinfo.value)
    assert "claude" in str(excinfo.value)
