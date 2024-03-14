from logging import getLogger
from typing import Optional

from chatbot.util.singleton import singleton
from .base import BaseEmbeddingModel

logger = getLogger(__name__)


@singleton
class EmbeddingModelFactory:
    """Embedding model factory"""

    def __init__(self) -> None:
        """Constructor"""
        logger.debug("__init__")
        self.models: dict[str, type] = {}

    def register(self, model: type):
        """Register model in factory"""
        logger.debug("register, model=%s", model)

        name: str = model.__name__
        self.models[name] = model

    def get(self, name: str) -> BaseEmbeddingModel:
        """Get model by name"""
        logger.debug("get, name=%s", name)
        model_class: Optional[type] = self.models.get(name)

        if model_class is None:
            raise RuntimeError(f"Model not found: {name}")

        model: Optional[BaseEmbeddingModel] = model_class()

        return model
