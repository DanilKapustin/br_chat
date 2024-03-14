from .factory import EmbeddingModelFactory
from .e5 import E5
from .base import BaseEmbeddingModel

factory: EmbeddingModelFactory = EmbeddingModelFactory()
factory.register(E5)

__all__ = [
    "factory",
    "BaseEmbeddingModel"
]
