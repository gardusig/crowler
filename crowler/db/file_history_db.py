from __future__ import annotations

import typer
from crowler.db.history_db import HistoryDB
from crowler.util.session_util import create_session_file


class FileHistoryStore:
    def __init__(self, name: str, pretty_label: str):
        self.name = name
        self._db: HistoryDB[list[str]] = HistoryDB(
            create_session_file(name),
            empty=[],
            normalise=lambda lst: sorted({p.strip() for p in lst if p.strip()}),
            pretty=lambda lst: (
                f"{pretty_label}:\n" + "\n".join(f"- {p}" for p in lst) or "(none)"
            ),
        )

    def _snap(self) -> list[str]:
        return list(self._db.latest())

    def clear(self) -> None:
        self._db.clear()

    def append(self, path: str) -> None:
        p = path.strip()
        if not p:
            typer.secho("⚠️  Empty path — nothing added.", fg="yellow")
            return
        files = self._snap()
        if p in files:
            typer.secho(f"⚠️  Path already present: {p}", fg="yellow")
            return
        files.append(p)
        self._db.push(files)

    def remove(self, path: str) -> None:
        p = path.strip()
        if not p:
            typer.secho("⚠️  Empty path — nothing removed.", fg="yellow")
            return
        files = self._snap()
        try:
            files.remove(p)
        except ValueError:
            typer.secho(f"⚠️  Path not tracked: {p}", fg="yellow")
            return
        self._db.push(files)

    def undo(self) -> None:
        if self._db.undo():
            typer.secho("↩️ Reverted last change.", fg="green")
        else:
            typer.secho("⚠️  Nothing to undo.", fg="yellow")

    def summary(self) -> str:
        return self._db.summary()

    def latest_set(self) -> set[str]:
        return set(self._db.latest())
