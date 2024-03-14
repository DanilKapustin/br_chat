from logging import getLogger
from typing import Optional

from chromadb import HttpClient, ClientAPI, Settings

from chatbot.config import CHROMA_HOST, CHROMA_PORT
from chatbot.util.singleton import singleton

logger = getLogger(__name__)


@singleton
class Connection:
    """Connection class"""

    HOST = "localhost"
    PORT = 7777

    def __init__(self) -> None:
        """Constructor"""
        logger.debug("__init__")

        self._client: Optional[ClientAPI] = HttpClient(
            CHROMA_HOST, CHROMA_PORT, settings=Settings(anonymized_telemetry=False)
        )

    @property
    def client(self) -> ClientAPI:
        """Get client"""
        logger.debug("client")
        return self._client
