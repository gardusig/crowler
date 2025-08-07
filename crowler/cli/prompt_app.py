from crowler.cli.app_factory import create_crud_app
from crowler.db.prompt_db import (
    append_prompt,
    remove_prompt,
    clear_prompts,
    summary_prompts,
    undo_prompts,
)


prompt_app = create_crud_app(
    name="prompt",
    help_text="Manage your prompt history",
    add_fn=append_prompt,
    remove_fn=remove_prompt,
    clear_fn=clear_prompts,
    list_fn=summary_prompts,
    undo_fn=undo_prompts,
    add_arg_name="prompt",
    add_arg_help="Prompt to append",
    remove_arg_name="prompt",
    remove_arg_help="Prompt to remove",
)
