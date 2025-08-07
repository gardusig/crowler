from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Union
from enum import Enum

from crowler.instruction.instruction_model import Instruction
from builtins import print

DEFAULT_FENCE = "~~~"
_FENCE_RE = re.escape(DEFAULT_FENCE)
QUOTES = "\"'`"


class TaskType(str, Enum):
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    GENERAL_DEVELOPMENT = "general_development"
    SINGLE_FILE = "single_file"


PATTERN_SETS = {
    TaskType.TEST_GENERATION: [
        r".*/tests?/.*test.*\.py$",
        r"^tests?/.*test.*\.py$",
        r"test.*\.py$",
        r".*_test\.py$",
    ],
    TaskType.DOCUMENTATION: [
        r"^README\.md$",
        r"^readme\.md$",
        r"^CHANGELOG\.md$",
        r"^changelog\.md$",
        r"\.md$",
    ],
    TaskType.GENERAL_DEVELOPMENT: [
        r"\.py$",
        r"^src/.*\.py$",
        r"^tests?/.*\.py$",
        r"\.md$",
    ],
    TaskType.SINGLE_FILE: [
        r"\.py$",
    ],
}

DEFAULT_ALLOWED_PATTERNS = PATTERN_SETS[TaskType.GENERAL_DEVELOPMENT]

CODE_BLOCK_RE = re.compile(
    rf"""
    {_FENCE_RE}                   # opening fence, optional indent
    (?P<quote>[{QUOTES}])              #   opening quote
    (?P<path>[^\r\n]+?)                #   path (no EOL)
    (?P=quote)                         #   closing quote
    (?P<body>.*?)                 # body (non-greedy)
    {_FENCE_RE}                   # closing fence, its own line
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def parse_code_response(
    response: str,
    root: Union[str, Path, None] = None,
    task_type: Optional[TaskType] = None,
    allowed_patterns: Optional[list[str]] = None,
) -> OrderedDict[str, str]:
    files: OrderedDict[str, str] = OrderedDict()
    base = Path(root).resolve() if root else None

    if allowed_patterns:
        patterns = allowed_patterns
    elif task_type:
        patterns = PATTERN_SETS.get(task_type, DEFAULT_ALLOWED_PATTERNS)
    else:
        patterns = DEFAULT_ALLOWED_PATTERNS

    filtered_count = 0
    allowed_regex = [re.compile(p) for p in patterns]

    for match in CODE_BLOCK_RE.finditer(response):
        raw_path = match.group("path").strip().strip(QUOTES)
        code = match.group("body")

        if not raw_path:
            continue

        norm = Path(raw_path).as_posix()

        if base and not (base / norm).resolve().is_relative_to(base):
            print(f"Rejected path outside root sandbox: {norm}")
            continue

        if not any(r.search(norm) for r in allowed_regex):
            print(f"Rejected file not matching allowed patterns: {norm}")
            filtered_count += 1
            continue

        if norm in files:
            print(f"Duplicate file path in response: {norm} (overwriting)")

        files[norm] = code

    if not files:
        print("No file/code blocks found in model response.")
    else:
        print(f"Decoded {len(files)} file(s) from model response.")
        print(f" Filtered out {filtered_count} file(s).")

    return files


def get_instruction_strings(
    instructions: Optional[list[Instruction]] = None,
) -> list[str]:
    instruction_strings: list[str] = []
    if instructions:
        for instruction in instructions:
            instruction_strings.extend(instruction.instructions)
    return instruction_strings
