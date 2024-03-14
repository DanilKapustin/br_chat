from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingModel(ABC):
    """Base embedding model class"""

    @abstractmethod
    async def generate_embedding(self, is_query: bool, text: str) -> List[float]:
        """Generate embedding from text"""
