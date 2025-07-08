from crowler.ai.ai_client_config import AIConfig
import pytest
from unittest.mock import patch, MagicMock

with (
    patch("crowler.ai.ai_client.get_shared_files", return_value=[]),
    patch("crowler.ai.ai_client.get_latest_prompts", return_value=[]),
    patch("crowler.ai.ai_client.stringify_file_contents", return_value=[]),
    patch("crowler.ai.ai_client.get_instruction_strings", return_value=[]),
):

    from crowler.ai.ai_client import AIClient


class DummyConfig(AIConfig):
    model = "dummy-model"
    temperature = 0.7
    top_p = 1.0
    max_tokens = 1000


class DummyInstruction:
    pass


class DummyAIClient(AIClient):
    def get_response(self, messages):
        return "dummy-response"

    def _get_shared_files(self):
        return []

    def _get_latest_prompts(self):
        return []

    def _stringify_file_contents(self, files, *args, **kwargs):
        return []

    def _get_instruction_strings(self, instructions):
        return []


@pytest.fixture
def ai_client():
    return DummyAIClient(DummyConfig())


@pytest.mark.parametrize(
    "instructions, prompt_files, final_prompt, shared_files, prompt_db, expected_roles",
    [
        ([[MagicMock(spec=DummyInstruction)]], None, None, [], [], ["system"]),
        (None, ["file1.txt"], None, [], [], ["user"]),
        (None, None, "final prompt", [], [], ["user"]),
        (
            [MagicMock(spec=DummyInstruction)],
            ["file1.txt", "file2.txt"],
            "final prompt",
            ["shared1.txt", "shared2.txt"],
            ["prompt1", "prompt2"],
            ["system", "user", "user", "user", "user"],
        ),
        (None, None, None, [], [], []),
    ],
)
def test_format_messages_various_inputs(
    ai_client,
    instructions,
    prompt_files,
    final_prompt,
    shared_files,
    prompt_db,
    expected_roles,
):
    with (
        patch(
            "crowler.ai.ai_client.get_instruction_strings",
            return_value=["instr1", "instr2"],
        ),
        patch("crowler.ai.ai_client.get_shared_files", return_value=shared_files),
        patch(
            "crowler.ai.ai_client.stringify_file_contents",
            side_effect=lambda files, *args, **kwargs: [f"content:{f}" for f in files],
        ),
        patch("crowler.ai.ai_client.get_latest_prompts", return_value=prompt_db),
    ):

        msgs = ai_client._format_messages(
            instructions=instructions,
            prompt_files=prompt_files,
            final_prompt=final_prompt,
        )
        assert [m["role"] for m in msgs] == expected_roles
        for msg in msgs:
            assert "role" in msg
            assert "content" in msg
            assert isinstance(msg["content"], str)


@pytest.mark.parametrize(
    "instructions, prompt_files, final_prompt, shared_files, prompt_db, expected_contents",
    [
        # Only shared files
        (None, None, None, ["shared1.txt"], [], ["content:shared1.txt"]),
        # Only prompt_files
        (None, ["promptfile.txt"], None, [], [], ["content:promptfile.txt"]),
        # Only prompt_db
        (None, None, None, [], ["prompt1"], ["prompt1"]),
        # Only final_prompt
        (None, None, "final prompt", [], [], ["final prompt"]),
    ],
)
def test_format_messages_content(
    ai_client,
    instructions,
    prompt_files,
    final_prompt,
    shared_files,
    prompt_db,
    expected_contents,
):
    with (
        patch("crowler.ai.ai_client.get_instruction_strings", return_value=["instr1"]),
        patch("crowler.ai.ai_client.get_shared_files", return_value=shared_files),
        patch(
            "crowler.ai.ai_client.stringify_file_contents",
            side_effect=lambda files, *args, **kwargs: [f"content:{f}" for f in files],
        ),
        patch("crowler.ai.ai_client.get_latest_prompts", return_value=prompt_db),
    ):

        msgs = ai_client._format_messages(
            instructions=instructions,
            prompt_files=prompt_files,
            final_prompt=final_prompt,
        )
        if msgs:
            assert msgs[-1]["content"].split("\n") == expected_contents


def test_send_message_calls_get_response_and_prints(monkeypatch, ai_client):
    # Patch _format_messages to return a known list
    messages = [
        {"role": "system", "content": "hello"},
        {"role": "user", "content": "world"},
    ]
    monkeypatch.setattr(ai_client, "_format_messages", lambda **kwargs: messages)
    # Patch get_response to check call and return value
    monkeypatch.setattr(ai_client, "get_response", lambda messages: "response123")
    result = ai_client.send_message()
    assert result == "response123"


def test_format_messages_with_none_inputs(ai_client):
    with (
        patch("crowler.ai.ai_client.get_instruction_strings", return_value=[]),
        patch("crowler.ai.ai_client.get_shared_files", return_value=[]),
        patch("crowler.ai.ai_client.stringify_file_contents", return_value=[]),
        patch("crowler.ai.ai_client.get_latest_prompts", return_value=[]),
    ):
        msgs = ai_client._format_messages(
            instructions=None,
            prompt_files=None,
            final_prompt=None,
        )
        assert msgs == []


def test_format_messages_with_multiple_shared_and_prompt_files(ai_client):
    with (
        patch("crowler.ai.ai_client.get_instruction_strings", return_value=[]),
        patch(
            "crowler.ai.ai_client.get_shared_files",
            return_value=["a.txt", "b.txt"],
        ),
        patch(
            "crowler.ai.ai_client.stringify_file_contents",
            side_effect=lambda files, *args, **kwargs: [f"file:{f}" for f in files],
        ),
        patch("crowler.ai.ai_client.get_latest_prompts", return_value=[]),
    ):
        msgs = ai_client._format_messages(
            instructions=None,
            prompt_files=["c.txt", "d.txt"],
            final_prompt=None,
        )
        # Should have two user messages: one for shared, one for prompt_files
        assert len(msgs) == 2
        assert msgs[0]["content"] == "file:a.txt\nfile:b.txt"
        assert msgs[1]["content"] == "file:c.txt\nfile:d.txt"


def test_format_messages_with_all_sections(ai_client):
    with (
        patch(
            "crowler.ai.ai_client.get_instruction_strings",
            return_value=["sys1", "sys2"],
        ),
        patch("crowler.ai.ai_client.get_shared_files", return_value=["s.txt"]),
        patch(
            "crowler.ai.ai_client.stringify_file_contents",
            side_effect=lambda files, *args, **kwargs: [f"sf:{f}" for f in files],
        ),
        patch("crowler.ai.ai_client.get_latest_prompts", return_value=["promptA"]),
    ):
        msgs = ai_client._format_messages(
            instructions=[MagicMock(spec=DummyInstruction)],
            prompt_files=["p.txt"],
            final_prompt="final!",
        )
        assert len(msgs) == 5
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert msgs[2]["role"] == "user"
        assert msgs[3]["role"] == "user"
        assert msgs[4]["role"] == "user"
        assert msgs[0]["content"] == "sys1\nsys2"
        assert msgs[1]["content"] == "sf:s.txt"
        assert msgs[2]["content"] == "sf:p.txt"
        assert msgs[3]["content"] == "promptA"
        assert msgs[4]["content"] == "final!"
