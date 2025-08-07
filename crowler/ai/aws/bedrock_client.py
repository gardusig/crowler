from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, cast

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from crowler.ai.ai_client_config import AIConfig
from crowler.ai.aws.bedrock_client_config import BedrockClientConfig

from crowler.ai.ai_client import AIClient

import typer


class BedrockClient(AIClient, ABC):
    MAX_TOKENS = 4096

    def __init__(
        self,
        config: AIConfig,
        region: str = "us-east-1",
        read_timeout: int = 300,
        connect_timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        super().__init__(config)
        try:
            boto_config = Config(
                region_name=region,
                read_timeout=read_timeout,
                connect_timeout=connect_timeout,
                retries={"max_attempts": max_retries},
            )
            self.client = boto3.client(
                "bedrock-runtime", region_name=region, config=boto_config
            )
        except (BotoCoreError, ClientError) as exc:
            typer.secho(
                f"❌ Unable to create Bedrock client: {exc}", fg="red", err=True
            )
            raise RuntimeError(f"Unable to create Bedrock client: {exc}") from exc

    @abstractmethod
    def _format_request_body(
        self,
        messages: list[dict[str, Any]],
    ) -> dict[str, Any]: ...

    @abstractmethod
    def _parse_response(
        self,
        raw: dict[str, Any],
    ) -> str: ...

    def get_response(self, messages: list[dict[str, Any]]) -> str:
        config = cast(BedrockClientConfig, self.config)
        body = self._format_request_body(
            messages=messages,
        )
        try:
            resp = self.client.invoke_model(
                modelId=config.model,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            typer.secho("✅ Received response from Bedrock", fg="green")
            payload = json.loads(resp["body"].read())
            result = self._parse_response(payload).strip()
            return result
        except (BotoCoreError, ClientError) as exc:
            typer.secho(f"❌ Bedrock request failed: {exc}", fg="red", err=True)
            raise RuntimeError(f"Bedrock request failed: {exc}") from exc
