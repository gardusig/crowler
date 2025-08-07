
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# Setup runner for all tests
runner = CliRunner()

def test_app_factory_creates_commands():
    """Test that app_factory correctly creates commands that call the provided functions"""
    from crowler.cli.app_factory import create_crud_app
    
    # Create mock functions
    mock_add = MagicMock(name="mock_add")
    mock_remove = MagicMock(name="mock_remove")
    mock_clear = MagicMock(name="mock_clear")
    mock_list = MagicMock(name="mock_list", return_value="Test list output")
    mock_undo = MagicMock(name="mock_undo")
    
    # Create an app using our mock functions
    app = create_crud_app(
        name="test",
        help_text="Test app",
        add_fn=mock_add,
        remove_fn=mock_remove,
        clear_fn=mock_clear,
        list_fn=mock_list,
        undo_fn=mock_undo,
        add_arg_name="item",
        add_arg_help="Item to add",
        remove_arg_name="item", 
        remove_arg_help="Item to remove"
    )
    
    # Test add command
    result = runner.invoke(app, ["add", "test_item"])
    assert result.exit_code == 0
    mock_add.assert_called_once_with("test_item")
    
    # Test remove command - verify remove_fn is called, not add_fn
    result = runner.invoke(app, ["remove", "test_item"])
    assert result.exit_code == 0
    # We need to patch app_factory.py to fix the bug where add_fn is called instead of remove_fn
    # But in our test, we should verify the expected behavior
    mock_remove.assert_called_once_with("test_item")
    
    # Test clear command
    result = runner.invoke(app, ["clear"])
    assert result.exit_code == 0
    mock_clear.assert_called_once()
    
    # Test list command
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    mock_list.assert_called_once()
    assert "Test list output" in result.output
    
    # Test undo command
    result = runner.invoke(app, ["undo"])
    assert result.exit_code == 0
    mock_undo.assert_called_once()

def test_prompt_app_created_with_correct_functions():
    """Test that prompt_app is created with the correct functions"""
    with patch('crowler.cli.app_factory.create_crud_app') as mock_create_app:
        # Save the original module
        import sys
        original_module = sys.modules.get('crowler.cli.prompt_app')
        
        # Remove module to force reload
        if 'crowler.cli.prompt_app' in sys.modules:
            del sys.modules['crowler.cli.prompt_app']
        
        # Import to trigger app creation
        import crowler.cli.prompt_app
        
        # Check that create_crud_app was called with the correct functions
        mock_create_app.assert_called_once()
        _, kwargs = mock_create_app.call_args
        
        assert kwargs['name'] == 'prompt'
        assert kwargs['help_text'] == 'Manage your prompt history'
        assert kwargs['add_fn'].__name__ == 'append_prompt'
        assert kwargs['remove_fn'].__name__ == 'remove_prompt'
        assert kwargs['clear_fn'].__name__ == 'clear_prompts'
        assert kwargs['list_fn'].__name__ == 'summary_prompts'
        assert kwargs['undo_fn'].__name__ == 'undo_prompts'
        assert kwargs['add_arg_name'] == 'prompt'
        assert kwargs['add_arg_help'] == 'Prompt to append'
        
        # Restore original module if it existed
        if original_module:
            sys.modules['crowler.cli.prompt_app'] = original_module

@pytest.fixture
def mock_prompt_store():
    """Create a mock for the prompt store"""
    store_mock = MagicMock()
    store_mock.summary.return_value = "📜 Prompts:\n- Test prompt"
    
    with patch('crowler.db.prompt_db._prompt_store', store_mock):
        yield store_mock

def test_prompt_db_append(mock_prompt_store):
    """Test that append_prompt delegates to the store's append method"""
    from crowler.db.prompt_db import append_prompt
    
    append_prompt("Test prompt")
    mock_prompt_store.append.assert_called_once_with("Test prompt")

def test_prompt_db_remove(mock_prompt_store):
    """Test that remove_prompt delegates to the store's remove method"""
    from crowler.db.prompt_db import remove_prompt
    
    remove_prompt("Test prompt")
    mock_prompt_store.remove.assert_called_once_with("Test prompt")

def test_prompt_db_clear(mock_prompt_store):
    """Test that clear_prompts delegates to the store's clear method"""
    from crowler.db.prompt_db import clear_prompts
    
    clear_prompts()
    mock_prompt_store.clear.assert_called_once()

def test_prompt_db_undo(mock_prompt_store):
    """Test that undo_prompts delegates to the store's undo method"""
    from crowler.db.prompt_db import undo_prompts
    
    undo_prompts()
    mock_prompt_store.undo.assert_called_once()

def test_prompt_db_summary(mock_prompt_store):
    """Test that summary_prompts delegates to the store's summary method"""
    from crowler.db.prompt_db import summary_prompts
    
    result = summary_prompts()
    mock_prompt_store.summary.assert_called_once()
    assert result == "📜 Prompts:\n- Test prompt"

def test_prompt_db_get_latest_prompts(mock_prompt_store):
    """Test that get_latest_prompts delegates to the store's latest method"""
    from crowler.db.prompt_db import get_latest_prompts
    
    mock_prompt_store.latest.return_value = ["Test prompt"]
    result = get_latest_prompts()
    mock_prompt_store.latest.assert_called_once()
    assert result == ["Test prompt"]
