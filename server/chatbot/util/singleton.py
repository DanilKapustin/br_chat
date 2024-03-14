from typing import Any, Optional


def singleton(cls):
    """Singleton decorator"""
    instances: dict[type, Any] = {}

    def get_instance(*args: Optional[Any], **kwargs: Optional[Any]) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)

        return instances[cls]

    return get_instance
