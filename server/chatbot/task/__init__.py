from .connection import queue
from .source import index_source

# TODO: make configurable from UI, per-task. Now it's 2 hours
TIMEOUT = 7200


async def enqueue(coroutine, **kwargs):
    """Enqueue task"""
    if "timeout" not in kwargs:
        kwargs.update({"timeout": TIMEOUT})

    return await queue.enqueue(coroutine.__name__, **kwargs)


__all__ = [
    "queue",
    "enqueue",
    "index_source",
]
