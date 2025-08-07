from dataclasses import dataclass
from typing import Optional
from crowler.ai.aws.bedrock_client_config import BedrockClientConfig

ANTHROPIC_VERSION: str = "bedrock-2023-05-31"


@dataclass
class ClaudeClientConfig(BedrockClientConfig):
    model: str
    max_tokens: int = 32000
    top_p: Optional[float] = None
    anthropic_version = ANTHROPIC_VERSION
    reasoning_max_tokens: Optional[int] = None
    temperature: float


@dataclass
class Claude35ClientConfig(ClaudeClientConfig):
    temperature: float = 0.24
    top_p: Optional[float] = 0.96
    model: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"


@dataclass
class Claude37ClientConfig(ClaudeClientConfig):
    temperature: float = 1
    reasoning_max_tokens: Optional[int] = 16000
    model: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"


@dataclass
class Claude4SonnetClientConfig(ClaudeClientConfig):
    temperature: float = 0.2
    top_p: Optional[float] = 0.9
    model: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"
