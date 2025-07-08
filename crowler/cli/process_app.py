from crowler.cli.app_factory import create_crud_app
from crowler.db.process_file_db import (
    append_processing_file,
    clear_processing_files,
    remove_processing_file,
    summary_processing_files,
    undo_processing_files,
)

process_app = create_crud_app(
    name="process",
    help_text="Manage your processing-file history",
    add_fn=append_processing_file,
    remove_fn=remove_processing_file,
    clear_fn=clear_processing_files,
    list_fn=summary_processing_files,
    undo_fn=undo_processing_files,
    add_arg_name="path",
    add_arg_help="Path to append",
    remove_arg_name="path",
    remove_arg_help="Path to remove",
    should_handle_filepaths=True,
)
