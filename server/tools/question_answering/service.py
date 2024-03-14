# ----------------------------------------------------------------------------
# Q&A algorithm.
# Result of this algo is an answer based on user question, matched data
# sources and previous session history
# ----------------------------------------------------------------------------
# 0. sources = search_documents(question)
# 1. answer = get_answer(session.messages, question, sources)
# 2. return answer
# ----------------------------------------------------------------------------

from datetime import datetime
from logging import getLogger
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.connection import get_db
from chatbot.db.model import Message, MessageSource, Session, Tool
from chatbot.dto import KnowledgeResult, MessageErrorResult, MessageResult
from chatbot.service import (
    knowledge as knowledge_service,
    session as session_service,
    tool as tool_service,
    model as model_service,
)
from chatbot.service.model import BaseModel, get_answer
from chatbot.service.session import message as message_service
from chatbot.service.tool.prompt import (
    build_prompt_with_history,
    check_prompt_fits_context_window,
)
from .configuration import Configuration

SUMMARY_GLUE = "\n----------\n"

logger = getLogger(__name__)


async def _search_sources(
    configuration: Configuration, question: str
) -> List[KnowledgeResult]:
    """Search sources"""
    logger.debug(
        "_search_sources, configuration=%s, question=%s", configuration, question
    )

    result: List[KnowledgeResult] = await knowledge_service.search(
        question, limit=configuration.max_results
    )
    logger.debug("_search_sources, matched sources=%s", result)

    return result


async def _compress_question(
    model: BaseModel,
    configuration: Configuration,
    history: list[Message],
    question: str,
) -> str:
    """Get compressed question based on previous history"""
    logger.debug(
        "_compress_question, model=%s, configuration=%s, history=%s, question=%s",
        model,
        configuration,
        history,
        question,
    )

    if len(history) == 0:
        return question

    max_prompt_length: int = (
        model.configuration.context_length - configuration.max_tokens
    )

    # get only 2 latest messages, to not distort the context too much
    messages: List[dict[str, str]] = build_prompt_with_history(
        model,
        history[-2:],
        configuration.prompt_compress_question.format(question=question),
        max_prompt_length,
    )

    return await get_answer(model, messages, configuration.max_tokens)


async def _build_prompt_with_sources(
    model: BaseModel,
    configuration: Configuration,
    question: str,
    sources: List[KnowledgeResult],
    max_prompt_length: int,
) -> str:
    """Build prompt with sources"""
    logger.debug(
        "_build_prompt_with_sources, model=%s, configuration=%s, question=%s, sources=%s, max_prompt_length=%s",
        model,
        configuration,
        question,
        sources,
        max_prompt_length,
    )

    prompt: Optional[str] = None

    # loop from 1 to len(sources) and try to build a prompt with given number of sources,
    # that fits into the allowed size
    for i in range(1, len(sources) + 1):
        logger.debug("_build_prompt_with_sources, trying sources=%s", i)
        prompt_candidate: str = configuration.prompt_answer.format(
            question=question,
            summaries=SUMMARY_GLUE.join([source.text for source in sources[:i]]),
        )

        if not check_prompt_fits_context_window(
            model, prompt_candidate, max_prompt_length
        ):
            logger.debug("_build_prompt_with_sources, prompt does not fit")
            break

        logger.debug("_build_prompt_with_sources, prompt fits")
        prompt = prompt_candidate

    if prompt is None:
        raise RuntimeError(
            "Cannot make prompt fit the context window with given sources"
        )

    return prompt


async def _question_and_answer_workflow(
    model: BaseModel,
    configuration: Configuration,
    history: list[Message],
    question: str,
) -> tuple[str, List[KnowledgeResult]]:
    """Q&A workflow"""
    logger.debug(
        "_question_and_answer_workflow, model=%s, configuration=%s, history=%s, question=%s",
        model,
        configuration,
        history,
        question,
    )

    # search sources
    search_question: str = await _compress_question(
        model, configuration, history, question
    )
    sources: List[KnowledgeResult] = await _search_sources(
        configuration, search_question
    )

    answer: Optional[str] = None

    if len(sources) > 0:
        max_prompt_length: int = (
            model.configuration.context_length - configuration.max_tokens
        )
        prompt: str = await _build_prompt_with_sources(
            model, configuration, question, sources, max_prompt_length
        )
        messages: List[dict[str, str]] = build_prompt_with_history(
            model, history, prompt, max_prompt_length
        )

        answer = await get_answer(model, messages, configuration.max_tokens)

    if answer is None:
        answer = configuration.answer_negative

    return answer, sources


async def _save_answer(
    db: AsyncSession,
    session_id: UUID,
    answer: str,
    sources: List[KnowledgeResult],
) -> Message:
    """Save answer"""
    logger.debug(
        "_save_answer, session_id=%s, answer=%s, sources=%s",
        session_id,
        answer,
        sources,
    )

    message_sources: List[MessageSource] = [
        MessageSource(id=uuid4(), **s.dict(include={"title", "url"})) for s in sources
    ]
    message: Message = await message_service.create(
        db, session_id, answer, sources=message_sources, is_system=True
    )

    return message


async def get_system_answer(user_id: UUID, session_id: UUID):
    """Get system answer for a dialog session"""
    logger.debug("get_system_answer, user_id=%s, session_id=%s", user_id, session_id)
    db: AsyncSession = await anext(get_db())

    try:
        session: Session = await session_service.get(db, user_id, session_id)
        history: list[Message] = list(
            await message_service.get_list(db, user_id, session_id, 0, 1000, False)
        )

        if len(history) == 0:
            raise RuntimeError("No messages in session")

        question: str = history[-1].message
        history = history[:-1]

        tool: Tool = await tool_service.get(db, session.tool_id)
        configuration: Configuration = Configuration(**tool.configuration)

        async with model_service.get_model_instance(db, tool.model_id) as model:
            answer: str
            sources: List[KnowledgeResult]

            answer, sources = await _question_and_answer_workflow(
                model, configuration, history, question
            )
            message: Message = await message_service.save_answer(
                db, user_id, session_id, answer, sources
            )

            # send message to UI
            message_to_user: str = MessageResult.from_orm(message).json()
            await message_service.publish(session_id, message_to_user)

    except Exception as err:
        logger.exception("Error generating response")

        message_to_user: str = MessageErrorResult(
            is_system=True,
            created_at=datetime.now(),
            created_by="system",
            message="Error generating response: " + str(err),
        ).json()

        await message_service.publish(session_id, message_to_user)

    finally:
        await db.close()
