from crowler.db.file_history_db import FileHistoryStore
import typer

_proc_store = FileHistoryStore("processing_history", "🔄 Processing files")


def clear_processing_files() -> None:
    _proc_store.clear()
    typer.secho("✅ Processing files cleared.", fg="green")


def append_processing_file(path: str) -> None:
    _proc_store.append(path)
    typer.secho(f"✅ Processing file appended: {path}", fg="green")


def remove_processing_file(path: str) -> None:
    _proc_store.remove(path)
    typer.secho(f"✅ Processing file removed: {path}", fg="green")


def undo_processing_files() -> None:
    _proc_store.undo()
    typer.secho("✅ Undo completed for processing files.", fg="green")


def summary_processing_files() -> str:
    summary = _proc_store.summary()
    return summary


def get_processing_files() -> set[str]:
    files = _proc_store.latest_set()
    return files
