from .base import BaseModel
from .model import *

logger = getLogger(__name__)


async def get_answer(
    model_: BaseModel, messages: List[dict[str, str]], max_tokens: int
) -> str:
    """Get answer depending on the model"""
    logger.debug(
        "get_answer, model=%s, messages=%s, max_tokens=%s",
        model_,
        len(messages),
        max_tokens,
    )

    answer: str = await model_.generate_answer(messages, max_tokens)
    logger.debug("get_answer, model=%s, answer=%s", model_, answer)

    return answer


__all__ = ["BaseModel", "get_answer"]
