import os
from typing import Callable, Optional

import typer

from crowler.ai.ai_client_config import AIConfig

from crowler.ai.ai_client import AIClient
from crowler.ai.aws.anthropic.claude_client import ClaudeClient
from crowler.ai.openai.openai_client import OpenAIClient


AI_CLIENTS: dict[str, Callable[[Optional[AIConfig]], AIClient]] = {
    "openai": OpenAIClient,
    "claude": ClaudeClient,
}


def get_ai_client(config: Optional[AIConfig] = None) -> AIClient:
    client_name = (os.getenv("AI_CLIENT") or "").strip().lower()
    if not client_name:
        typer.secho("❌ AI_CLIENT environment variable not set.", fg="red", err=True)
        raise RuntimeError("⛔️ AI_CLIENT environment variable not set.")
    try:
        client = AI_CLIENTS[client_name](config)
        return client
    except KeyError as exc:
        typer.secho(
            f'❌ Unsupported AI_CLIENT "{client_name}". '
            f"Supported: {list(AI_CLIENTS.keys())}",
            fg="red",
            err=True,
        )
        raise ValueError(
            f"❌ Unsupported AI_CLIENT '{client_name}'. "
            f"Supported: {list(AI_CLIENTS.keys())}"
        ) from exc
