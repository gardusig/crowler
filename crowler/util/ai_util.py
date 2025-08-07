from typing import Any, Optional, Union
from crowler.db.shared_file_db import get_shared_files

from crowler.db.prompt_db import get_latest_prompts
from crowler.util.file_util import stringify_file_contents

from crowler.util.string_util import get_instruction_strings

from crowler.instruction.instruction_model import Instruction
from pathlib import Path


def format_messages(
    instructions: Optional[list[Instruction]] = None,
    prompt_files: Optional[Union[list[str], list[Path]]] = None,
    final_prompt: Optional[str] = None,
) -> list[dict[str, Any]]:
    msgs: list[dict[str, Any]] = []

    if instructions:
        instruction_strings = get_instruction_strings(instructions)
        msgs.append(
            {
                "role": "system",
                "content": "\n".join(instruction_strings),
            }
        )

    user_parts = []

    shared_files = get_shared_files()
    if shared_files:
        shared_files_content = stringify_file_contents(
            list(shared_files), "File context"
        )
        user_parts.append("\n".join(shared_files_content))

    prompts = get_latest_prompts()
    if prompts:
        user_parts.append("\n".join(prompts))

    if prompt_files:
        prompt_files_content = stringify_file_contents(prompt_files)
        user_parts.append("\n".join(prompt_files_content))

    if final_prompt:
        user_parts.append(final_prompt)

    if user_parts:
        msgs.append(
            {
                "role": "user",
                "content": "\n\n".join(user_parts),
            }
        )

    return msgs
