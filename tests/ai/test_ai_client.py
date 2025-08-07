import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from crowler.ai.ai_client import AIClient
from crowler.ai.ai_client_config import AIConfig
from crowler.instruction.instruction_model import Instruction


class MockAIConfig(AIConfig):
    """Mock implementation of AIConfig for testing"""

    model = "test-model"
    temperature = 0.5
    top_p = 0.9
    max_tokens = 500


class MockAIClient(AIClient):
    """Mock implementation of AIClient for testing"""

    def get_response(self, messages):
        return f"Response to {len(messages)} messages"


@pytest.fixture
def ai_client():
    return MockAIClient(MockAIConfig())


def test_init():
    config = MockAIConfig()
    client = MockAIClient(config)
    assert client.config == config
    assert client.config.model == "test-model"
    assert client.config.temperature == 0.5


def test_send_message_with_all_arguments(ai_client, monkeypatch):
    # Test data
    mock_instructions = [MagicMock(spec=Instruction)]
    mock_prompt_files = ["file1.txt", "file2.txt"]
    mock_final_prompt = "final prompt"

    formatted_messages = [
        {"role": "system", "content": "system content"},
        {"role": "user", "content": "user content"},
    ]

    # Mock format_messages
    mock_format = MagicMock(return_value=formatted_messages)
    monkeypatch.setattr("crowler.ai.ai_client.format_messages", mock_format)

    # Mock get_response
    mock_response = MagicMock(return_value="Test response")
    monkeypatch.setattr(ai_client, "get_response", mock_response)

    # Call send_message
    result = ai_client.send_message(
        instructions=mock_instructions,
        prompt_files=mock_prompt_files,
        final_prompt=mock_final_prompt,
    )

    # Verify format_messages was called correctly
    mock_format.assert_called_once_with(
        instructions=mock_instructions,
        prompt_files=mock_prompt_files,
        final_prompt=mock_final_prompt,
    )

    # Verify get_response was called with the formatted messages
    mock_response.assert_called_once_with(messages=formatted_messages)

    # Verify the result
    assert result == "Test response"


def test_send_message_with_default_arguments(ai_client, monkeypatch):
    # Mock format_messages
    formatted_messages = []
    mock_format = MagicMock(return_value=formatted_messages)
    monkeypatch.setattr("crowler.ai.ai_client.format_messages", mock_format)

    # Mock get_response
    mock_response = MagicMock(return_value="Empty response")
    monkeypatch.setattr(ai_client, "get_response", mock_response)

    # Call send_message with default arguments
    result = ai_client.send_message()

    # Verify format_messages was called correctly with None arguments
    mock_format.assert_called_once_with(
        instructions=None, prompt_files=None, final_prompt=None
    )

    # Verify get_response was called with empty messages
    mock_response.assert_called_once_with(messages=[])

    # Verify the result
    assert result == "Empty response"


def test_send_message_with_path_objects(ai_client, monkeypatch):
    # Test with Path objects for prompt_files
    path_files = [Path("file1.txt"), Path("file2.txt")]

    formatted_messages = [{"role": "user", "content": "file content"}]
    mock_format = MagicMock(return_value=formatted_messages)
    monkeypatch.setattr("crowler.ai.ai_client.format_messages", mock_format)

    mock_response = MagicMock(return_value="Path response")
    monkeypatch.setattr(ai_client, "get_response", mock_response)

    result = ai_client.send_message(prompt_files=path_files)

    mock_format.assert_called_once_with(
        instructions=None, prompt_files=path_files, final_prompt=None
    )
    assert result == "Path response"


def test_send_message_error_handling(ai_client, monkeypatch):
    # Mock format_messages to raise an exception
    mock_format = MagicMock(side_effect=ValueError("Format error"))
    monkeypatch.setattr("crowler.ai.ai_client.format_messages", mock_format)

    # Test that the exception is propagated
    with pytest.raises(ValueError, match="Format error"):
        ai_client.send_message()

    # Mock format_messages to succeed but get_response to fail
    mock_format = MagicMock(return_value=[{"role": "user", "content": "test"}])
    monkeypatch.setattr("crowler.ai.ai_client.format_messages", mock_format)

    mock_response = MagicMock(side_effect=RuntimeError("API error"))
    monkeypatch.setattr(ai_client, "get_response", mock_response)

    with pytest.raises(RuntimeError, match="API error"):
        ai_client.send_message()


def test_abstract_methods():
    # AIClient is abstract and requires get_response to be implemented
    config = MockAIConfig()

    # Should raise TypeError when trying to instantiate abstract class
    with pytest.raises(TypeError):
        AIClient(config)  # This should fail because get_response is abstract
