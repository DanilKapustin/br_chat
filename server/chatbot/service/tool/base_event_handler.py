from abc import ABC, abstractmethod
from typing import Callable, Coroutine, TypeAlias
from uuid import UUID


class BaseEventHandler(ABC):
    """Base event handler"""

    @abstractmethod
    async def on_session_created(self, user_id: UUID, session_id: UUID, message: str):
        """Called when a new session is created"""

    @abstractmethod
    async def on_session_finished(self, user_id: UUID, session_id: UUID):
        """Called when a session is finished"""


EventHandlerMethod: TypeAlias = Callable[
    [BaseEventHandler, dict[str, object]], Coroutine
]
