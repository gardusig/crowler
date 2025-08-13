from unittest.mock import Mock, call, patch
from crowler.cli.app_factory import create_crud_app
from typer.testing import CliRunner

runner = CliRunner()


def test_create_crud_app_add_command_calls_add_fn():
    mock_add = Mock()
    mock_remove = Mock()
    mock_clear = Mock()
    mock_list = Mock(return_value="list output")
    mock_undo = Mock()

    app = create_crud_app(
        name="test",
        help_text="Test app",
        add_fn=mock_add,
        remove_fn=mock_remove,
        clear_fn=mock_clear,
        list_fn=mock_list,
        undo_fn=mock_undo,
        should_handle_filepaths=False,
    )

    # Invoke the add command with a single arg
    result = runner.invoke(app, ["add", "item1"])

    assert result.exit_code == 0
    mock_add.assert_called_once_with("item1")


def test_create_crud_app_add_command_handles_filepaths():
    mock_add = Mock()
    mock_remove = Mock()
    mock_clear = Mock()
    mock_list = Mock(return_value="list output")
    mock_undo = Mock()

    app = create_crud_app(
        name="test",
        help_text="Test app",
        add_fn=mock_add,
        remove_fn=mock_remove,
        clear_fn=mock_clear,
        list_fn=mock_list,
        undo_fn=mock_undo,
        should_handle_filepaths=True,
    )

    # Patch get_all_files to simulate multiple files
    with patch(
        "crowler.cli.app_factory.get_all_files", return_value=["file1", "file2"]
    ):
        result = runner.invoke(app, ["add", "folder"])

    assert result.exit_code == 0
    mock_add.assert_has_calls([call("file1"), call("file2")])


def test_create_crud_app_clear_command_calls_clear_fn():
    mock_add = Mock()
    mock_remove = Mock()
    mock_clear = Mock()
    mock_list = Mock(return_value="list output")
    mock_undo = Mock()

    app = create_crud_app(
        name="test",
        help_text="Test app",
        add_fn=mock_add,
        remove_fn=mock_remove,
        clear_fn=mock_clear,
        list_fn=mock_list,
        undo_fn=mock_undo,
    )

    result = runner.invoke(app, ["clear"])
    assert result.exit_code == 0
    mock_clear.assert_called_once()


def test_create_crud_app_list_command_calls_list_fn_and_outputs(monkeypatch):
    mock_add = Mock()
    mock_remove = Mock()
    mock_clear = Mock()
    mock_list = Mock(return_value="list output")
    mock_undo = Mock()

    app = create_crud_app(
        name="test",
        help_text="Test app",
        add_fn=mock_add,
        remove_fn=mock_remove,
        clear_fn=mock_clear,
        list_fn=mock_list,
        undo_fn=mock_undo,
    )

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    mock_list.assert_called_once()
    assert "list output" in result.output
