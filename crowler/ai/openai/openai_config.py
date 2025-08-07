from dataclasses import dataclass
from typing import Optional

from crowler.ai.ai_client_config import AIConfig


@dataclass
class OpenAIConfig(AIConfig):
    model: str = "gpt-4.1"
    temperature: float = 0.24
    max_tokens: int = 4096 * 2
    top_p: Optional[float] = 0.96
