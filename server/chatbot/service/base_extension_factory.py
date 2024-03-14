from abc import ABC
from importlib.machinery import ModuleSpec
from importlib.util import spec_from_file_location, module_from_spec
from logging import getLogger
from os import path
from types import ModuleType
from typing import cast, Type

from pydantic import BaseModel

from chatbot.util.file import get_subdirectories

logger = getLogger(__name__)


class BaseExtensionFactory(ABC):
    """Base extension factory"""

    EXTENSIONS_DIR: str = "extensions"

    def __init__(self):
        """Constructor"""
        logger.debug("__init__")
        self._extensions: list[str] = []

        # cache containing {module_name -> {extension_name -> module}}
        self._module_cache: dict[str, dict[str, ModuleType]] = {}

    def _get_extensions(self) -> list[str]:
        """Get a list of available extensions

        Returns a list of extension names
        """
        logger.debug("_get_extensions")

        if len(self._extensions) > 0:
            return self._extensions

        self._extensions = get_subdirectories(self.EXTENSIONS_DIR)

        return self._extensions

    def _get_extension_modules(self, module_name: str) -> dict[str, ModuleType]:
        """Get extension modules

        Returns a dictionary containing {extension_name -> module}
        """
        logger.debug("_get_extension_modules, module_name=%s", module_name)

        if module_name in self._module_cache:
            return self._module_cache[module_name]

        self._module_cache[module_name] = {}

        for extension in self._get_extensions():
            logger.debug("_get_extension_modules, loading for extension=%s", extension)

            module_path: str = path.join(
                self.EXTENSIONS_DIR, extension, f"{module_name}.py"
            )
            spec: ModuleSpec = spec_from_file_location(
                f"{self.EXTENSIONS_DIR}.{extension}.{module_name}", module_path
            )
            module: ModuleType = module_from_spec(spec)
            spec.loader.exec_module(module)

            self._module_cache[module_name][extension] = module

        return self._module_cache[module_name]

    def _get_module_attributes(
        self, module_name: str, attribute: str
    ) -> dict[str, object]:
        """Get module attributes

        Returns a dictionary containing {extension_name -> attribute}
        """
        logger.debug(
            "_get_module_attributes, module_name=%s, attribute=%s",
            module_name,
            attribute,
        )
        result: dict[str, object] = {}

        for extension, module in self._get_extension_modules(module_name).items():
            reference: object = getattr(module, attribute, None)

            if reference is None:
                raise NotImplementedError(
                    f"Extension module {extension}.{module_name} has no {attribute} definition"
                )

            result[extension] = reference

        return result

    def get_configuration_classes(self) -> dict[str, Type[BaseModel]]:
        """Get configuration classes"""
        logger.debug("get_configuration_classes")
        return cast(
            dict[str, Type[BaseModel]],
            self._get_module_attributes("configuration", "Configuration"),
        )

    def get_configuration_class(self, name: str) -> Type[BaseModel]:
        """Get configuration class"""
        logger.debug("get_configuration_class, name=%s", name)
        configuration_class: Type[BaseModel] = self.get_configuration_classes().get(
            name
        )

        if configuration_class is None:
            raise NotImplementedError(
                f"Extension configuration not implemented: {name}"
            )

        return configuration_class
