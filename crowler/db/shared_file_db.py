from crowler.db.file_history_db import FileHistoryStore
import typer

_shared_store = FileHistoryStore("file_set_history", "📁 Shared files")


def clear_shared_files() -> None:
    _shared_store.clear()
    typer.secho("✅ Shared files cleared.", fg="green")


def append_shared_file(path: str) -> None:
    _shared_store.append(path)
    typer.secho(f"✅ Shared file appended: {path}", fg="green")


def remove_shared_file(path: str) -> None:
    _shared_store.remove(path)
    typer.secho(f"✅ Shared file removed: {path}", fg="green")


def undo_shared_files() -> None:
    _shared_store.undo()
    typer.secho("✅ Undo completed for shared files.", fg="green")


def summary_shared_files() -> str:
    summary = _shared_store.summary()
    return summary


def get_shared_files() -> set[str]:
    files = _shared_store.latest_set()
    return files
