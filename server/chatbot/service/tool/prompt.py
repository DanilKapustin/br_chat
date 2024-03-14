from logging import getLogger

from chatbot.db.model import Message
from chatbot.service.model import BaseModel

ROLE_ASSISTANT = "assistant"
ROLE_USER = "user"

logger = getLogger(__name__)


def check_prompt_fits_context_window(
    model: BaseModel, prompt: str, max_prompt_length: int
) -> bool:
    """Check if prompt fits the context window"""
    logger.debug(
        "check_prompt_fits_context_window, prompt=%s, max_prompt_length=%s",
        prompt[:20] + "..." + prompt[-20:],
        max_prompt_length,
    )

    try:
        build_prompt(model, prompt, max_prompt_length)
        return True

    except ValueError:
        return False


def build_prompt(
    model: BaseModel, prompt: str, max_prompt_length: int
) -> list[dict[str, str]]:
    """Build prompt messages"""
    logger.debug(
        "build_prompt, model=%s, prompt=%s, max_prompt_length=%s",
        model,
        prompt[:20] + "..." + prompt[-20:],
        max_prompt_length,
    )

    messages: list[dict[str, str]] = [{"role": ROLE_USER, "content": prompt}]
    token_count: int = model.get_token_count(messages)
    logger.debug("build_prompt, token_count=%s", token_count)

    if token_count > max_prompt_length:
        raise ValueError(
            "Prompt token count exceeds context window, prompt=%s, token_count=%s, max_prompt_length=%s"
            % (prompt, token_count, max_prompt_length)
        )

    return messages


def build_prompt_with_history(
    model: BaseModel, history: list[Message], prompt: str, max_prompt_length: int
) -> list[dict[str, str]]:
    """Build prompt messages by connecting history messages and new prompt"""
    logger.debug(
        "build_prompt_with_history, model=%s, history=%s, prompt=%s, max_prompt_length=%s",
        model,
        len(history),
        prompt[:20] + "..." + prompt[-20:],
        max_prompt_length,
    )

    # add messages starting from the last one
    messages: list[dict[str, str]] = [{"role": ROLE_USER, "content": prompt}]
    token_count: int = model.get_token_count(messages)
    logger.debug(
        "build_prompt_with_history, latest message token_count=%s", token_count
    )

    if token_count >= max_prompt_length:
        raise ValueError(
            "Prompt token count exceeds context window, prompt=%s, token_count=%s, max_prompt_length=%s"
            % (prompt, token_count, max_prompt_length)
        )

    for ctr, message in enumerate(reversed(history)):
        candidate: dict[str, str] = {
            "role": ROLE_ASSISTANT if message.is_system else ROLE_USER,
            "content": message.message,
        }

        try_messages: list[dict[str, str]] = [candidate] + messages
        token_count = model.get_token_count(try_messages)
        logger.debug(
            "build_prompt_with_history, history message=%s/%s, token_count=%s, max_prompt_length=%s",
            ctr + 1,
            len(history),
            token_count,
            max_prompt_length,
        )

        if token_count >= max_prompt_length:
            logger.debug(
                "build_prompt_with_history, token_count=%s, max_prompt_length=%s exceeded",
                token_count,
                max_prompt_length,
            )
            break

        messages = try_messages

    return messages
