from typing import Optional

from chatbot.dto import ModelConfiguration


class Configuration(ModelConfiguration):
    """Saiga-2 configuration"""

    path: str
    context_length: int = 4096
    top_k: int = 100
    top_p: float = 1.0
    repeat_penalty: float = 1.0
    gpu_layers: int = 0
    threads: int = 4
    prompt_system: Optional[str]
