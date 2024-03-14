from logging import getLogger
from typing import Optional, Type, cast

from chatbot.dto import ModelConfiguration
from chatbot.util.singleton import singleton
from .base import BaseModel
from ..base_extension_factory import BaseExtensionFactory

MODELS_DIR = "models"

logger = getLogger(__name__)


@singleton
class ModelFactory(BaseExtensionFactory):
    """Model factory"""

    EXTENSIONS_DIR = "models"

    def __init__(self) -> None:
        """Constructor"""
        logger.debug("__init__")

        super().__init__()

        self._model_classes: dict[str, Type[BaseModel]] = cast(
            dict[str, Type[BaseModel]],
            self._get_module_attributes("model", "Model"),
        )

        self._model_cache: dict[tuple[str, tuple], BaseModel] = {}

    def _get_key(
        self, name: str, configuration: ModelConfiguration
    ) -> tuple[str, tuple]:
        """Get key for model cache"""
        return (
            name,
            tuple(configuration.dict().items()),
        )

    def get_model_class(self, name: str) -> Optional[Type[BaseModel]]:
        """Get model class by name"""
        logger.debug("get_model_class, name=%s", name)
        return self._model_classes.get(name)

    def get(self, name: str, configuration: ModelConfiguration) -> BaseModel:
        """Get model by name and configuration"""
        logger.debug("get, name=%s, configuration=%s", name, configuration)
        key: tuple[str, tuple] = self._get_key(name, configuration)

        if key in self._model_cache:
            return self._model_cache[key]

        # unload other local models, if any - now we can only work one model at a time
        for key in list(self._model_cache.keys()):
            if self._model_cache[key].IS_LOCAL:
                del self._model_cache[key]

        model_class: Optional[Type[BaseModel]] = self._model_classes.get(name)

        if model_class is None:
            raise ValueError(f"Model not found: {name}")

        model: BaseModel = model_class(configuration)
        self._model_cache[self._get_key(name, configuration)] = model

        return model
