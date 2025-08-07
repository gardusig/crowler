from dataclasses import dataclass
from typing import Optional

from crowler.ai.ai_client_config import AIConfig


@dataclass
class BedrockClientConfig(AIConfig):
    model: str
    temperature: float
    top_p: Optional[float]
    max_tokens: int
