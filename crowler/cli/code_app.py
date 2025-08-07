from typing import OrderedDict
from crowler.instruction.instructions.typer_log import TYPER_LOG_INSTRUCTION
from crowler.instruction.instructions.mypy import MYPY_INSTRUCTION
from crowler.instruction.instructions.readme import README_INSTRUCTION
from crowler.db.process_file_db import get_processing_files
from crowler.util.file_util import rewrite_files
from crowler.instruction.instructions.response_format import RESPONSE_FORMAT_INSTRUCTION
from crowler.instruction.instructions.unit_test import UNIT_TEST_INSTRUCTION
from crowler.ai.ai_client_factory import get_ai_client
from crowler.util.string_util import TaskType, parse_code_response
import typer

code_app = typer.Typer(
    name="code",
    invoke_without_command=True,
)


@code_app.command("unit-test")
def create_unit_tests(
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip prompts and overwrite tests unconditionally.",
    ),
):
    for filepath in get_processing_files():
        try:
            create_unit_test(force, filepath)
        except Exception as e:
            typer.secho(
                f"❌ Failed to create test for {filepath!r}: {e}",
                fg="red",
                err=True,
            )


def create_unit_test(force: bool, filepath: str):
    if filepath.endswith("__init__.py"):
        typer.secho(f"⚠️  Skipping __init__.py file: {filepath}", fg="yellow")
        return
    ai_client = get_ai_client()
    response = ai_client.send_message(
        instructions=[
            RESPONSE_FORMAT_INSTRUCTION,
            UNIT_TEST_INSTRUCTION,
        ],
        prompt_files=[filepath],
        final_prompt=f'Focus only on creating|fixing test(s) for "{filepath}"',
    )
    file_map = parse_code_response(
        response=response,
        task_type=TaskType.TEST_GENERATION,
    )
    for path, content in file_map.items():
        if not filepath.endswith(path):
            continue
        rewrite_files(
            files=OrderedDict({filepath: content}),
            force=force,
        )


@code_app.command("readme")
def create_readme(
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip prompts and overwrite tests unconditionally.",
    ),
):
    ai_client = get_ai_client()
    try:
        response = ai_client.send_message(
            instructions=[
                RESPONSE_FORMAT_INSTRUCTION,
                README_INSTRUCTION,
            ],
            prompt_files=["./README.md"],
            final_prompt='Focus only on creating a single "README.md"',
        )
        file_map = parse_code_response(response)
        rewrite_files(files=file_map, force=force)
    except Exception as e:
        typer.secho(
            f"❌ Failed to create README.md: {e}",
            fg="red",
            err=True,
        )


@code_app.command("mypy")
def fix_mypy_errors(
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip prompts and overwrite tests unconditionally.",
    ),
):
    ai_client = get_ai_client()
    for filepath in get_processing_files():
        try:
            response = ai_client.send_message(
                instructions=[
                    RESPONSE_FORMAT_INSTRUCTION,
                    MYPY_INSTRUCTION,
                ],
                prompt_files=[filepath],
                final_prompt=f"Focus on fixing only mypy errors related to {filepath}",
            )
            file_map = parse_code_response(response)
            rewrite_files(files=file_map, force=force)
        except Exception as e:
            typer.secho(
                f"❌ Failed to fix mypy errors for {filepath!r}: {e}",
                fg="red",
                err=True,
            )


@code_app.command("typer-log")
def improve_typer_logs(
    force: bool = typer.Option(
        False,
        "--force",
        help="Skip prompts and overwrite tests unconditionally.",
    ),
):
    ai_client = get_ai_client()
    for filepath in get_processing_files():
        if filepath.endswith("__init__.py"):
            typer.secho(f"⚠️  Skipping __init__.py file: {filepath}", fg="yellow")
            continue
        try:
            response = ai_client.send_message(
                instructions=[
                    RESPONSE_FORMAT_INSTRUCTION,
                    TYPER_LOG_INSTRUCTION,
                ],
                prompt_files=[filepath],
                final_prompt=f"Focus on only {filepath}",
            )
            file_map = parse_code_response(response)
            rewrite_files(files=file_map, force=force)
        except Exception as e:
            typer.secho(
                f"❌ Failed to improve typer logs for {filepath!r}: {e}",
                fg="red",
                err=True,
            )
