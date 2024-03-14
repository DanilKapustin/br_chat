from abc import ABC, abstractmethod
from logging import getLogger
from typing import List

from chatbot.dto import ModelConfiguration

logger = getLogger(__name__)


class BaseModel(ABC):
    """Base model class"""

    IS_LOCAL: bool = False

    def __init__(self, configuration: ModelConfiguration):
        """Constructor"""
        if not isinstance(configuration, ModelConfiguration):
            raise TypeError("configuration must be an instance of ModelConfiguration")

        self._configuration: ModelConfiguration = configuration

    @abstractmethod
    def get_token_count(self, messages: List[dict[str, str]]) -> int:
        """Return the number of tokens used by a list of messages."""

    @abstractmethod
    async def generate_answer(
        self, messages: List[dict[str, str]], max_tokens: int
    ) -> str:
        """Generate answer for given messages"""

    @property
    def configuration(self) -> ModelConfiguration:
        """Return model configuration"""
        return self._configuration

    def __repr__(self):
        """Return string representation"""
        return f"{self.__class__.__name__}"
