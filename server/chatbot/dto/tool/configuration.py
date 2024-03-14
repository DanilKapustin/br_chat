from typing import Any

from pydantic import BaseModel


class ToolConfigurationFields(BaseModel):
    """Tool configuration description"""

    name: str
    fields: dict[str, Any]


class ToolConfiguration(BaseModel):
    """Tool configuration"""

    def dict(self, *args, **kwargs):
        result: dict = super().dict(*args, **kwargs)

        for k, v in result.items():
            result[k] = str(v)

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}()"
