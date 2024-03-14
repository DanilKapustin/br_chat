from typing import Any

from pydantic import BaseModel


class ModelConfigurationFields(BaseModel):
    """Model type configuration description"""

    name: str
    fields: dict[str, Any]


class ModelConfiguration(BaseModel):
    """Base model configuration"""

    temperature: float = 0.2
    context_length: int = 128

    def dict(self, *args, **kwargs):
        """Get dictionary representation"""
        result: dict = super().dict(*args, **kwargs)

        for k, v in result.items():
            result[k] = str(v)

        return result
