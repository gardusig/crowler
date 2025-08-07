from crowler.db.shared_file_db import (
    append_shared_file,
    clear_shared_files,
    remove_shared_file,
    summary_shared_files,
    undo_shared_files,
)
from crowler.cli.app_factory import create_crud_app

file_app = create_crud_app(
    name="file",
    help_text="Manage your shared-file history",
    add_fn=append_shared_file,
    remove_fn=remove_shared_file,
    clear_fn=clear_shared_files,
    list_fn=summary_shared_files,
    undo_fn=undo_shared_files,
    add_arg_name="path",
    add_arg_help="Path to append",
    remove_arg_name="path",
    remove_arg_help="Path to remove",
    should_handle_filepaths=True,
)
