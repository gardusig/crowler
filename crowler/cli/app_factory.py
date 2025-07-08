import typer
from crowler.util.file_util import get_all_files


def create_crud_app(
    name: str,
    help_text: str,
    add_fn,
    remove_fn,
    clear_fn,
    list_fn,
    undo_fn,
    add_arg_name="item",
    add_arg_help="Item to add",
    remove_arg_name="item",
    remove_arg_help="Item to remove",
    should_handle_filepaths=False,
):
    app = typer.Typer(name=name, help=help_text)

    @app.command("add")
    def add_command(arg: str = typer.Argument(..., help=add_arg_help)):
        """Add an item."""
        try:
            if should_handle_filepaths:
                for item in get_all_files(arg):
                    add_fn(item)
            else:
                add_fn(arg)
        except Exception as e:
            typer.secho(f"❌ Failed to add {add_arg_name}: {e}", fg="red", err=True)
            raise

    @app.command("remove")
    def remove_command(arg: str = typer.Argument(..., help=remove_arg_help)):
        """Remove an item."""
        try:
            if should_handle_filepaths:
                for item in get_all_files(arg):
                    remove_fn(item)
            else:
                add_fn(arg)
        except Exception as e:
            typer.secho(
                f"❌ Failed to remove {remove_arg_name}: {e}", fg="red", err=True
            )
            raise

    @app.command("clear")
    def clear_command():
        """Clear all items."""
        try:
            clear_fn()
        except Exception as e:
            typer.secho(f"❌ Failed to clear {name}: {e}", fg="red", err=True)
            raise

    @app.command("list")
    def list_command():
        """List all items."""
        try:
            summary = list_fn()
            typer.echo(summary)
        except Exception as e:
            typer.secho(f"❌ Failed to list {name}: {e}", fg="red", err=True)
            raise

    @app.command("undo")
    def undo_command():
        """Undo last change."""
        try:
            undo_fn()
        except Exception as e:
            typer.secho(f"❌ Failed to undo last change: {e}", fg="red", err=True)
            raise

    return app
