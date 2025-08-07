from __future__ import annotations
from typing import Any, Optional, cast

from crowler.ai.ai_client_config import AIConfig

from crowler.ai.aws.anthropic.claude_client_config import (
    Claude37ClientConfig,
    ClaudeClientConfig,
)
from crowler.ai.aws.bedrock_client import BedrockClient

import typer


class ClaudeClient(BedrockClient):
    def __init__(self, config: Optional[AIConfig] = None):
        if not config:
            config = Claude37ClientConfig()
        super().__init__(config)

    def _format_request_body(
        self,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.config = cast(ClaudeClientConfig, self.config)

        system_content = None
        user_assistant_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                user_assistant_messages.append(msg)

        request_body = {
            "anthropic_version": self.config.anthropic_version,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": user_assistant_messages,
        }

        if system_content:
            request_body["system"] = system_content
        if self.config.top_p:
            request_body["top_p"] = self.config.top_p
        if self.config.reasoning_max_tokens:
            request_body["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.config.reasoning_max_tokens,
            }
        return request_body

    def _parse_response(self, raw: dict[str, Any]) -> str:
        try:
            text_content = None
            for content_item in raw["content"]:
                if content_item["type"] == "text":
                    text_content = content_item["text"]
                elif content_item["type"] == "thinking":
                    _ = content_item["thinking"]
            if text_content:
                return text_content
            else:
                typer.secho(
                    "⚠️ No text content found in response", fg="yellow", err=True
                )
                return str(raw)
        except Exception as e:
            typer.secho(f"❌ Failed to parse Claude response: {e}", fg="red", err=True)
            typer.secho(
                f"Response structure: {str(raw)[:500]}...", fg="yellow", err=True
            )
            raise
