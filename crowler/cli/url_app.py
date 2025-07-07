import typer
from crowler.cli.app_factory import create_crud_app
from crowler.db.url_db import (
    append_url,
    clear_urls,
    get_urls,
    remove_url,
    summary_urls,
    undo_urls,
)
from crowler.util.html_util import extract_html_data

url_app = create_crud_app(
    name="url",
    help_text="Manage your URL history",
    add_fn=append_url,
    remove_fn=remove_url,
    clear_fn=clear_urls,
    list_fn=summary_urls,
    undo_fn=undo_urls,
    add_arg_name="link",
    add_arg_help="Link to append",
    remove_arg_name="link",
    remove_arg_help="Link to remove",
)


@url_app.command("parse")
def parse_urls():
    """Undo the last change to your HTML URL history."""
    for url in get_urls():
        try:
            data = extract_html_data(url)
            print(data)
        except Exception as e:
            typer.secho(f"❌ Failed to undo last change: {e}", fg="red", err=True)
            raise
