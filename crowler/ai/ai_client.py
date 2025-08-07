from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

import typer
from crowler.util.ai_util import format_messages

from crowler.instruction.instruction_model import Instruction

from crowler.ai.ai_client_config import AIConfig

from abc import ABC, abstractmethod


class AIClient(ABC):
    def __init__(self, config: AIConfig):
        self.config = config

    @abstractmethod
    def get_response(self, messages: Any) -> str:
        pass

    def send_message(
        self,
        instructions: Optional[list[Instruction]] = None,
        prompt_files: Optional[Union[list[str], list[Path]]] = None,
        final_prompt: Optional[str] = None,
    ) -> str:
        try:
            messages = format_messages(
                instructions=instructions,
                prompt_files=prompt_files,
                final_prompt=final_prompt,
            )
            typer.secho("Sending message to AI client...")
            response = self.get_response(
                messages=messages,
            )
            return response
        except Exception as e:
            typer.secho(
                f"❌ Failed to send message to AI client: {e}", fg="red", err=True
            )
            raise
