import pytest

import crowler.ai.aws.anthropic.claude_client_config as claude_client_config


class DummyBedrockClientConfig:
    def __init__(self, *args, **kwargs):
        pass


@pytest.fixture(autouse=True)
def patch_bedrock_client_config(monkeypatch):
    # Patch BedrockClientConfig in the module under test to avoid dependency
    monkeypatch.setattr(
        claude_client_config, "BedrockClientConfig", DummyBedrockClientConfig
    )


def test_anthropic_version_constant():
    assert claude_client_config.ANTHROPIC_VERSION == "bedrock-2023-05-31"


def test_claude_client_config_inherits(monkeypatch):
    # Confirm inheritance and field assignment
    config = claude_client_config.ClaudeClientConfig(
        model="test-model", temperature=0.25
    )
    assert isinstance(config, claude_client_config.ClaudeClientConfig)
    assert config.model == "test-model"
    assert config.anthropic_version == claude_client_config.ANTHROPIC_VERSION


def test_claude35_client_config_defaults():
    config = claude_client_config.Claude35ClientConfig()
    assert isinstance(config, claude_client_config.Claude35ClientConfig)
    assert config.model == "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    assert config.anthropic_version == claude_client_config.ANTHROPIC_VERSION
    assert config.temperature == 0.24
    assert config.top_p == 0.96


def test_claude37_client_config_defaults():
    config = claude_client_config.Claude37ClientConfig()
    assert isinstance(config, claude_client_config.Claude37ClientConfig)
    assert config.model == "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    assert config.anthropic_version == claude_client_config.ANTHROPIC_VERSION
    assert config.temperature == 1
    assert config.reasoning_max_tokens == 16000


def test_claude4_sonnet_client_config_defaults():
    config = claude_client_config.Claude4SonnetClientConfig()
    assert isinstance(config, claude_client_config.Claude4SonnetClientConfig)
    assert config.model == "us.anthropic.claude-sonnet-4-20250514-v1:0"
    assert config.anthropic_version == claude_client_config.ANTHROPIC_VERSION
    assert config.temperature == 0.2
    assert config.top_p == 0.9


@pytest.mark.parametrize(
    "cls,expected_model",
    [
        (
            claude_client_config.Claude35ClientConfig,
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        ),
        (
            claude_client_config.Claude37ClientConfig,
            "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        ),
        (
            claude_client_config.Claude4SonnetClientConfig,
            "us.anthropic.claude-sonnet-4-20250514-v1:0",
        ),
    ],
)
def test_model_defaults_for_subclasses(cls, expected_model):
    config = cls()
    assert config.model == expected_model


def test_claude_client_config_optional_fields():
    config = claude_client_config.ClaudeClientConfig(
        model="test-model", temperature=0.5
    )
    assert config.max_tokens == 32000
    assert config.top_p is None
    assert config.reasoning_max_tokens is None


def test_claude_client_config_with_reasoning():
    config = claude_client_config.Claude37ClientConfig()
    assert config.reasoning_max_tokens == 16000

    config_no_reasoning = claude_client_config.Claude35ClientConfig()
    assert config_no_reasoning.reasoning_max_tokens is None
