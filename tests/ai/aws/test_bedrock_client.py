import pytest
from unittest.mock import MagicMock

import sys


# Patch all external dependencies at import time
@pytest.fixture(autouse=True)
def patch_external_deps(monkeypatch):
    # Patch boto3 and botocore exceptions
    mock_boto3 = MagicMock()
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client
    monkeypatch.setitem(sys.modules, "boto3", mock_boto3)
    mock_botocore_exceptions = MagicMock()

    class DummyBotoCoreError(Exception):
        pass

    class DummyClientError(Exception):
        pass

    mock_botocore_exceptions.BotoCoreError = DummyBotoCoreError
    mock_botocore_exceptions.ClientError = DummyClientError
    monkeypatch.setitem(sys.modules, "botocore.exceptions", mock_botocore_exceptions)
    # Patch crowler.ai.ai_client_config.AIConfig
    monkeypatch.setitem(sys.modules, "crowler.ai.ai_client_config", MagicMock())
    # Patch crowler.ai.aws.bedrock_client_config.BedrockClientConfig
    monkeypatch.setitem(
        sys.modules, "crowler.ai.aws.bedrock_client_config", MagicMock()
    )
    # Patch crowler.ai.ai_client.AIClient
    monkeypatch.setitem(sys.modules, "crowler.ai.ai_client", MagicMock())
    yield


import crowler.ai.aws.bedrock_client as bedrock_client_mod


class DummyConfig:
    model = "dummy-model"


class DummyBedrockClient(bedrock_client_mod.BedrockClient):
    def _format_request_body(self, messages):
        return {"messages": messages}

    def _parse_response(self, raw):
        return raw.get("output", "")


@pytest.fixture
def dummy_config():
    return DummyConfig()


def test_init_success(monkeypatch, dummy_config):
    # Patch boto3.client to succeed
    mock_boto3 = MagicMock()
    mock_client = MagicMock()
    mock_boto3.client.return_value = mock_client

    # Mock Config class
    mock_config_class = MagicMock()
    mock_config_instance = MagicMock()
    mock_config_class.return_value = mock_config_instance

    monkeypatch.setattr(bedrock_client_mod, "boto3", mock_boto3)
    monkeypatch.setattr(bedrock_client_mod, "Config", mock_config_class)

    client = DummyBedrockClient(config=dummy_config)
    assert hasattr(client, "client")

    # Verify Config was created with correct parameters
    mock_config_class.assert_called_once()
    config_kwargs = mock_config_class.call_args[1]
    assert config_kwargs["region_name"] == "us-east-1"
    assert config_kwargs["read_timeout"] == 300
    assert config_kwargs["connect_timeout"] == 30
    assert config_kwargs["retries"] == {"max_attempts": 3}

    # Verify boto3.client was called with correct parameters
    mock_boto3.client.assert_called_once_with(
        "bedrock-runtime", region_name="us-east-1", config=mock_config_instance
    )


def test_init_failure(monkeypatch, dummy_config):
    # Patch boto3.client to raise BotoCoreError
    class DummyBotoCoreError(Exception):
        pass

    monkeypatch.setattr(
        bedrock_client_mod,
        "boto3",
        MagicMock(client=MagicMock(side_effect=DummyBotoCoreError("fail"))),
    )
    monkeypatch.setattr(bedrock_client_mod, "BotoCoreError", DummyBotoCoreError)
    with pytest.raises(RuntimeError) as excinfo:
        DummyBedrockClient(config=dummy_config)
    assert "Unable to create Bedrock client" in str(excinfo.value)


@pytest.mark.parametrize(
    "messages, response_body, expected_output",
    [
        ([{"role": "user", "content": "hi"}], {"output": "Hello!"}, "Hello!"),
        ([{"role": "user", "content": "bye"}], {"output": "Goodbye!"}, "Goodbye!"),
        ([{"role": "user", "content": "empty"}], {"output": ""}, ""),
    ],
)
def test_get_response_success(
    monkeypatch, dummy_config, messages, response_body, expected_output
):
    # Patch boto3 client
    mock_client = MagicMock()
    mock_resp = {"body": MagicMock()}
    import json

    mock_resp["body"].read.return_value = json.dumps(response_body)
    mock_client.invoke_model.return_value = mock_resp

    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_client
    monkeypatch.setattr(bedrock_client_mod, "boto3", mock_boto3)

    # Mock Config class
    mock_config = MagicMock()
    monkeypatch.setattr(bedrock_client_mod, "Config", mock_config)

    # Patch BedrockClientConfig for cast
    monkeypatch.setattr(bedrock_client_mod, "BedrockClientConfig", type(dummy_config))
    # Patch print to builtins.print to silence output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    client = DummyBedrockClient(config=dummy_config)
    result = client.get_response(messages)
    assert result == expected_output
    mock_client.invoke_model.assert_called_once()
    args, kwargs = mock_client.invoke_model.call_args
    assert kwargs["modelId"] == dummy_config.model
    assert kwargs["contentType"] == "application/json"
    assert kwargs["accept"] == "application/json"


def test_get_response_boto_error(monkeypatch, dummy_config):
    # Patch boto3 client to raise error on invoke_model
    class DummyBotoCoreError(Exception):
        pass

    mock_client = MagicMock()
    mock_client.invoke_model.side_effect = DummyBotoCoreError("fail")

    mock_boto3 = MagicMock()
    mock_boto3.client.return_value = mock_client
    monkeypatch.setattr(bedrock_client_mod, "boto3", mock_boto3)

    # Mock Config class
    mock_config = MagicMock()
    monkeypatch.setattr(bedrock_client_mod, "Config", mock_config)

    monkeypatch.setattr(bedrock_client_mod, "BedrockClientConfig", type(dummy_config))
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    monkeypatch.setattr(bedrock_client_mod, "BotoCoreError", DummyBotoCoreError)
    client = DummyBedrockClient(config=dummy_config)
    with pytest.raises(RuntimeError) as excinfo:
        client.get_response([{"role": "user", "content": "fail"}])
    assert "Bedrock request failed" in str(excinfo.value)
