from __future__ import annotations

import typer
from crowler.db.history_db import HistoryDB
from crowler.util.session_util import create_session_file


class UrlHistoryStore:
    def __init__(self, name: str, pretty_label: str):
        self.name = name
        self._db: HistoryDB[list[str]] = HistoryDB(
            create_session_file(name),
            empty=[],
            normalise=lambda urls: sorted({url.strip() for url in urls if url.strip()}),
            pretty=lambda urls: (
                f"{pretty_label}:\n" + "\n".join(f"- {url}" for url in urls) or "(none)"
            ),
        )

    def _snap(self) -> list[str]:
        return list(self._db.latest())

    def clear(self) -> None:
        self._db.clear()

    def append(self, url: str) -> None:
        u = url.strip()
        if not u:
            typer.secho("⚠️  Empty URL — nothing added.", fg="yellow")
            return
        urls = self._snap()
        if u in urls:
            typer.secho(f"⚠️  URL already present: {u}", fg="yellow")
            return
        urls.append(u)
        self._db.push(urls)

    def remove(self, url: str) -> None:
        u = url.strip()
        if not u:
            typer.secho("⚠️  Empty URL — nothing removed.", fg="yellow")
            return
        urls = self._snap()
        try:
            urls.remove(u)
        except ValueError:
            typer.secho(f"⚠️  URL not tracked: {u}", fg="yellow")
            return
        self._db.push(urls)

    def undo(self) -> None:
        if self._db.undo():
            typer.secho("↩️ Reverted last change.", fg="green")
        else:
            typer.secho("⚠️  Nothing to undo.", fg="yellow")

    def summary(self) -> str:
        return self._db.summary()

    def latest_set(self) -> set[str]:
        return set(self._db.latest())


# ───── instantiate the store ────────────────────────────

_store = UrlHistoryStore("history", "🌐 URLs")


# ───── public API for URLs ───────────────────────────────


def clear_urls() -> None:
    _store.clear()
    typer.secho("✅ URLs cleared.", fg="green")


def append_url(url: str) -> None:
    _store.append(url)
    typer.secho(f"✅ URL appended: {url}", fg="green")


def remove_url(url: str) -> None:
    _store.remove(url)
    typer.secho(f"✅ URL removed: {url}", fg="green")


def undo_urls() -> None:
    _store.undo()
    typer.secho("✅ Undo completed for URLs.", fg="green")


def summary_urls() -> str:
    summary = _store.summary()
    return summary


def get_urls() -> set[str]:
    urls = _store.latest_set()
    return urls
