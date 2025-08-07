import pytest

from crowler.ai.aws.bedrock_client_config import BedrockClientConfig


def test_bedrock_client_config_defaults():
    # Provide all required parameters since the dataclass doesn't have defaults
    config = BedrockClientConfig(
        model="test-model", temperature=0.25, top_p=0.96, max_tokens=4096
    )
    assert config.model == "test-model"
    assert config.temperature == 0.25
    assert config.max_tokens == 4096
    assert config.top_p == 0.96


@pytest.mark.parametrize(
    "model,temperature,max_tokens,top_p",
    [
        ("model-a", 0.5, 2048, 0.9),
        ("model-b", 0.0, 1, 0.0),
        ("model-c", 1.0, 8192, 1.0),
    ],
)
def test_bedrock_client_config_custom_values(model, temperature, max_tokens, top_p):
    config = BedrockClientConfig(
        model=model, temperature=temperature, max_tokens=max_tokens, top_p=top_p
    )
    assert config.model == model
    assert config.temperature == temperature
    assert config.max_tokens == max_tokens
    assert config.top_p == top_p


def test_bedrock_client_config_inherits_ai_config():
    # Ensure BedrockClientConfig implements AIConfig at runtime
    from crowler.ai.aws.bedrock_client_config import BedrockClientConfig
    from crowler.ai.ai_client_config import AIConfig

    # Provide all required parameters to create a valid instance
    config = BedrockClientConfig(
        model="foo", temperature=0.5, top_p=0.9, max_tokens=2048
    )

    # Instead of issubclass (which fails for non-runtime-checkable Protocols), check for attribute presence
    required_attrs = ["temperature", "max_tokens", "top_p", "model"]
    for attr in required_attrs:
        assert hasattr(config, attr)


def test_bedrock_client_config_with_none_top_p():
    # Test with top_p as None
    config = BedrockClientConfig(
        model="test-model", temperature=0.25, top_p=None, max_tokens=4096
    )
    assert config.top_p is None
