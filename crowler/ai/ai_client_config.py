from typing import Optional, Protocol


class AIConfig(Protocol):
    model: str
    temperature: float
    top_p: Optional[float]
    max_tokens: int
