import re
from dataclasses import dataclass
from typing import List, Pattern


def _compile(patterns: List[str]) -> List[Pattern]:
    return [re.compile(p) for p in patterns]


@dataclass
class Instruction:
    instructions: List[str]
    allow_file_patterns: List[Pattern]
    deny_file_patterns: List[Pattern]

    def __init__(
        self,
        instructions: List[str],
        allow_file_patterns: List[str] = [],
        deny_file_patterns: List[str] = [],
    ):
        self.instructions = instructions
        self.allow_file_patterns = _compile(allow_file_patterns)
        self.deny_file_patterns = _compile(deny_file_patterns)
