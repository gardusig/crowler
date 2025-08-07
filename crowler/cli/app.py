from __future__ import annotations

from crowler.ai.ai_client_factory import get_ai_client

from crowler.db.url_db import clear_urls, summary_urls
from crowler.db.process_file_db import (
    clear_processing_files,
    summary_processing_files,
)
from crowler.db.shared_file_db import clear_shared_files, summary_shared_files
from crowler.db.prompt_db import append_prompt, clear_prompts, summary_prompts

import typer
import pyperclip
from pyperclip import PyperclipException

from crowler.cli.code_app import code_app
from crowler.cli.process_app import process_app
from crowler.cli.prompt_app import prompt_app
from crowler.cli.file_app import file_app
from crowler.cli.url_app import url_app

app = typer.Typer()
app.add_typer(code_app)
app.add_typer(file_app)
app.add_typer(process_app)
app.add_typer(prompt_app)
app.add_typer(url_app)


# ───────────────────────── helpers ────────────────────────── #


def _clipboard_get() -> str:
    try:
        typer.secho("ℹ️  Attempting to read from clipboard…", fg="green")
        result = pyperclip.paste()
        typer.secho("✅ Clipboard read successfully.", fg="green")
        return result
    except pyperclip.PyperclipException:
        typer.secho("❌  Clipboard not available on this system.", fg="red", err=True)
        raise typer.Exit(1)


def _clipboard_set(text: str) -> None:
    try:
        typer.secho("ℹ️  Attempting to write to clipboard…", fg="green")
        pyperclip.copy(text)
        typer.secho("✅ Clipboard updated successfully.", fg="green")
    except PyperclipException:
        typer.echo(text)
        typer.secho(
            "⚠️  Clipboard not available; printed instead.", fg="yellow", err=True
        )


def summary_all() -> str:
    not_empty_summary_list = []
    summary_list = [
        summary_prompts(),
        summary_shared_files(),
        summary_processing_files(),
        summary_urls(),
    ]
    for summary in summary_list:
        if summary:
            not_empty_summary_list.append(summary)
    return "\n".join(not_empty_summary_list)


# ───────────────────────── commands ───────────────────────── #


@app.command(name="show")
def preview():
    summary_list = summary_all()
    if not summary_list:
        typer.echo("Empty")
        return
    typer.echo(summary_list)


@app.command(name="copy")
def copy_to_clipboard():
    _clipboard_set(summary_all())


@app.command(name="paste")
def add_prompt_from_clipboard():
    append_prompt(_clipboard_get())


@app.command(name="clear")
def clear_all():
    clear_prompts()
    clear_shared_files()
    clear_processing_files()
    clear_urls()


@app.command("ask")
def ask():
    ai_client = get_ai_client()
    response = ai_client.send_message()
    typer.echo(response)
