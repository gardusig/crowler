from __future__ import annotations

import typer
from crowler.db.history_db import HistoryDB
from crowler.util.session_util import create_session_file


class PromptHistoryStore:
    def __init__(self, name: str, pretty_label: str):
        self.name = name
        self._db: HistoryDB[list[str]] = HistoryDB(
            create_session_file(self.name),
            empty=[],
            normalise=lambda lines: [ln.strip() for ln in lines if ln.strip()],
            pretty=lambda lines: (
                f"{pretty_label}:\n"
                + ("\n".join(f"- {ln}" for ln in lines) if lines else "(none)")
            ),
        )

    def _snap(self) -> list[str]:
        """Get a mutable copy of the latest prompt list."""
        return list(self._db.latest())

    def clear(self) -> None:
        self._db.clear()
        typer.secho("✅ Prompt history cleared", fg="green")

    def append(self, prompt: str) -> None:
        p = prompt.strip()
        if not p:
            typer.secho("⚠️  Empty prompt — nothing added.", fg="yellow")
            return
        items = self._snap()
        if p in items:
            typer.secho(f"⚠️  Prompt already present: {p}", fg="yellow")
            return
        items.append(p)
        self._db.push(items)
        typer.secho("✅ Added prompt", fg="green")

    def remove(self, prompt: str) -> None:
        p = prompt.strip()
        if not p:
            typer.secho("⚠️  Empty prompt — nothing removed.", fg="yellow")
            return
        items = self._snap()
        try:
            items.remove(p)
        except ValueError:
            typer.secho(f"⚠️  Prompt not tracked: {p}", fg="yellow")
            return
        self._db.push(items)
        typer.secho(f"✅ Removed prompt: {p}", fg="green")

    def undo(self) -> None:
        if self._db.undo():
            typer.secho("✅ Reverted last prompt change.", fg="green")
        else:
            typer.secho("⚠️  Nothing to undo.", fg="yellow")

    def summary(self) -> str:
        return self._db.summary()

    def latest(self) -> list[str]:
        """Convenience for modules that need the current prompts."""
        return list(self._db.latest())


# ───── instantiate your prompt‐store ────────────────────────────

_prompt_store = PromptHistoryStore("prompt_history", "📜 Prompts")


# ───── public API for prompts ───────────────────────────────────


def clear_prompts() -> None:
    _prompt_store.clear()


def append_prompt(line: str) -> None:
    _prompt_store.append(line)


def remove_prompt(line: str) -> None:
    _prompt_store.remove(line)


def undo_prompts() -> None:
    _prompt_store.undo()


def summary_prompts() -> str:
    summary = _prompt_store.summary()
    return summary


def get_latest_prompts() -> list[str]:
    latest = _prompt_store.latest()
    return latest
