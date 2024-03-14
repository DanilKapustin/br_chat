from logging import getLogger
from types import ModuleType
from typing import cast, Coroutine
from inspect import getmembers, isfunction

from fastapi import APIRouter

from chatbot.util.singleton import singleton
from .base_event_handler import BaseEventHandler
from ..base_extension_factory import BaseExtensionFactory

TOOLS_DIR = "tools"

logger = getLogger(__name__)


@singleton
class ToolFactory(BaseExtensionFactory):
    """Tool factory singleton"""

    EXTENSIONS_DIR = "tools"
    _instance: "ToolFactory" = None

    def get_api_routers(self) -> dict[str, APIRouter]:
        """Get API routers"""
        logger.debug("get_api_routers")
        return cast(dict[str, APIRouter], self._get_module_attributes("api", "router"))

    def get_task_entry_points(self) -> dict[str, Coroutine]:
        """Get task entry points"""
        logger.debug("get_task_entry_points")

        task_modules: dict[str, ModuleType] = self._get_extension_modules("task")
        results: dict[str, Coroutine] = {}

        for module_name, module in task_modules.items():
            for name, coroutine in getmembers(module, isfunction):
                if name.startswith("run_"):
                    results[module_name] = coroutine

        logger.debug("get_task_entry_points, results=%s", results)

        return results

    def get_event_handlers(self) -> dict[str, BaseEventHandler]:
        """Get event handlers"""
        logger.debug("get_event_handlers")
        return cast(
            dict[str, BaseEventHandler],
            self._get_module_attributes("event", "EventHandler"),
        )

    def get_event_handler(self, name: str) -> BaseEventHandler:
        """Get event handler"""
        logger.debug("get_event_handler, name=%s", name)
        event_handler: BaseEventHandler = self.get_event_handlers().get(name)

        if event_handler is None:
            raise NotImplementedError("Tool not implemented: " + name)

        return event_handler
