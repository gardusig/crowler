import pytest
from unittest.mock import patch, MagicMock

# Patch external dependencies at the top-level of the module under test
patch_target_create_session_file = "crowler.db.prompt_db.create_session_file"
patch_target_HistoryDB = "crowler.db.prompt_db.HistoryDB"


@pytest.fixture(autouse=True)
def patch_external_deps(monkeypatch):
    """Patch external dependencies for all tests."""
    # Patch create_session_file to return a dummy file path
    monkeypatch.setattr(
        "crowler.db.prompt_db.create_session_file", lambda name: f"/tmp/{name}.json"
    )
    # Patch HistoryDB with a MagicMock
    mock_history_db_cls = MagicMock()
    monkeypatch.setattr("crowler.db.prompt_db.HistoryDB", mock_history_db_cls)
    yield


@pytest.fixture
def prompt_store():
    """Create a fresh PromptHistoryStore for tests."""
    from crowler.db import prompt_db

    return prompt_db.PromptHistoryStore("test_history", "Test Prompts")


@pytest.fixture
def mock_db():
    """Get a PromptHistoryStore with a mocked _db for fine-grained control."""
    from crowler.db import prompt_db

    store = prompt_db.PromptHistoryStore("test_history", "Test Prompts")
    mock_db = MagicMock()
    store._db = mock_db
    return store, mock_db


def test_store_initialization(monkeypatch):
    """Test proper initialization of PromptHistoryStore."""
    from crowler.db import prompt_db

    # Create a PromptHistoryStore with mocked HistoryDB
    mock_historydb_cls = MagicMock()
    monkeypatch.setattr("crowler.db.prompt_db.HistoryDB", mock_historydb_cls)

    store = prompt_db.PromptHistoryStore("test_name", "Test Label")

    # Check initialization
    assert store.name == "test_name"

    # Check HistoryDB initialization
    mock_historydb_cls.assert_called_once()

    # Extract and test normalise function
    kwargs = mock_historydb_cls.call_args[1]
    normalise_fn = kwargs["normalise"]
    assert normalise_fn(["  test  ", "", "  test2"]) == ["test", "test2"]

    # Test pretty function formatting
    pretty_fn = kwargs["pretty"]
    formatted = pretty_fn(["item1", "item2"])
    assert "Test Label" in formatted
    assert "- item1" in formatted
    assert "- item2" in formatted


@pytest.mark.parametrize(
    "input_lines,expected",
    [
        (["prompt1", "prompt2"], ["prompt1", "prompt2"]),
        ([], []),
        (["  prompt1  ", "   ", "prompt2"], ["  prompt1  ", "   ", "prompt2"]),
    ],
)
def test_snap_returns_clean_copy(mock_db, input_lines, expected):
    """Test that _snap() returns a clean copy of the latest prompt list."""
    store, mock_db_instance = mock_db
    mock_db_instance.latest.return_value = input_lines

    result = store._snap()

    assert result == expected
    assert result is not input_lines  # Should be a copy


def test_clear_calls_db_and_prints(mock_db, capsys):
    """Test that clear() calls the db's clear method and prints confirmation."""
    store, mock_db_instance = mock_db

    store.clear()

    mock_db_instance.clear.assert_called_once()
    out = capsys.readouterr().out
    assert "cleared" in out
    assert "✅" in out  # Check for success indicator


@pytest.mark.parametrize(
    "prompt,existing,expected_push,expected_msg",
    [
        ("new prompt", [], ["new prompt"], "Added prompt"),
        ("", [], None, "Empty prompt"),
        ("   ", ["something"], None, "Empty prompt"),
        ("dupe", ["dupe"], None, "already present"),
        ("new with spaces", ["other"], ["other", "new with spaces"], "Added prompt"),
    ],
)
def test_append_prompt(mock_db, capsys, prompt, existing, expected_push, expected_msg):
    """Test append() with various inputs and existing states."""
    store, mock_db_instance = mock_db
    mock_db_instance.latest.return_value = existing

    store.append(prompt)

    out = capsys.readouterr().out
    if expected_push is not None:
        mock_db_instance.push.assert_called_once_with(expected_push)
        assert expected_msg in out
        assert "✅" in out  # Success indicator
    else:
        mock_db_instance.push.assert_not_called()
        assert expected_msg in out
        assert "⚠️" in out  # Warning indicator


@pytest.mark.parametrize(
    "prompt,existing,expected_push,expected_msg",
    [
        ("to_remove", ["to_remove", "other"], ["other"], "Removed prompt"),
        ("", ["to_remove"], None, "Empty prompt"),
        ("not_present", ["a", "b"], None, "not tracked"),
        (
            "  to_remove  ",
            ["to_remove", "other"],
            ["other"],
            "Removed prompt",
        ),  # With whitespace
    ],
)
def test_remove_prompt(mock_db, capsys, prompt, existing, expected_push, expected_msg):
    """Test remove() with various inputs and existing states."""
    store, mock_db_instance = mock_db
    mock_db_instance.latest.return_value = existing.copy()

    store.remove(prompt)

    out = capsys.readouterr().out
    if expected_push is not None:
        mock_db_instance.push.assert_called_once_with(expected_push)
        assert expected_msg in out
        assert "✅" in out  # Success indicator
    else:
        mock_db_instance.push.assert_not_called()
        assert expected_msg in out
        assert "⚠️" in out  # Warning indicator


@pytest.mark.parametrize(
    "undo_result,expected_msg,expected_indicator",
    [
        (True, "Reverted", "✅"),
        (False, "Nothing to undo", "⚠️"),
    ],
)
def test_undo_prompts(mock_db, capsys, undo_result, expected_msg, expected_indicator):
    """Test undo() with successful and unsuccessful cases."""
    store, mock_db_instance = mock_db
    mock_db_instance.undo.return_value = undo_result

    store.undo()

    out = capsys.readouterr().out
    assert expected_msg in out
    assert expected_indicator in out


def test_summary_delegates(mock_db):
    """Test that summary() correctly delegates to db's summary method."""
    store, mock_db_instance = mock_db
    mock_db_instance.summary.return_value = "summary!"

    result = store.summary()

    assert result == "summary!"
    mock_db_instance.summary.assert_called_once()


def test_latest_delegates(mock_db):
    """Test that latest() correctly delegates to db's latest method."""
    store, mock_db_instance = mock_db
    mock_db_instance.latest.return_value = ["a", "b"]

    result = store.latest()

    assert result == ["a", "b"]
    mock_db_instance.latest.assert_called_once()


def test_public_api_functions(monkeypatch):
    """Test that the public API functions correctly delegate to _prompt_store."""
    from crowler.db import prompt_db

    # Patch _prompt_store methods
    monkeypatch.setattr(prompt_db._prompt_store, "clear", MagicMock())
    monkeypatch.setattr(prompt_db._prompt_store, "append", MagicMock())
    monkeypatch.setattr(prompt_db._prompt_store, "remove", MagicMock())
    monkeypatch.setattr(prompt_db._prompt_store, "undo", MagicMock())
    monkeypatch.setattr(
        prompt_db._prompt_store, "summary", MagicMock(return_value="sum")
    )
    monkeypatch.setattr(
        prompt_db._prompt_store, "latest", MagicMock(return_value=["x"])
    )

    # Test each public API function
    prompt_db.clear_prompts()
    prompt_db._prompt_store.clear.assert_called_once()

    prompt_db.append_prompt("foo")
    prompt_db._prompt_store.append.assert_called_once_with("foo")

    prompt_db.remove_prompt("bar")
    prompt_db._prompt_store.remove.assert_called_once_with("bar")

    prompt_db.undo_prompts()
    prompt_db._prompt_store.undo.assert_called_once()

    assert prompt_db.summary_prompts() == "sum"
    prompt_db._prompt_store.summary.assert_called_once()

    assert prompt_db.get_latest_prompts() == ["x"]
    prompt_db._prompt_store.latest.assert_called_once()
