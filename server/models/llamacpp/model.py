from logging import getLogger
from typing import List

from llama_cpp import ChatCompletion, Llama

from chatbot.service.model import BaseModel
from .configuration import Configuration

DEFAULT_CHAT_FORMAT = "llama2"

logger = getLogger(__name__)


class Model(BaseModel):
    """Llama.cpp-based model"""

    IS_LOCAL: bool = True

    def __init__(self, configuration: Configuration):
        """Constructor"""
        super().__init__(configuration)

        logger.info("__init__, loading model")
        chat_format: str = configuration.chat_format

        if chat_format is None or chat_format == "":
            chat_format = DEFAULT_CHAT_FORMAT

        self._configuration: Configuration = configuration
        self._model: Llama = Llama(
            model_path=configuration.path,
            n_ctx=configuration.context_length,
            n_parts=1,
            n_threads=configuration.threads,
            n_gpu_layers=configuration.gpu_layers,
            n_batch=512,
            chat_format=chat_format,
        )

    def __del__(self):
        """Destructor"""
        logger.info("__del__, unloading model")
        del self._model

    def get_token_count(self, messages: List[dict[str, str]]) -> int:
        """Return the number of tokens used by a list of messages."""
        logger.debug("get_token_count, self=%s, messages=%s", self, len(messages))

        tokens_per_message: int = 3
        token_count: int = 0

        for message in messages:
            token_count += tokens_per_message

            for key, value in message.items():
                token_count += len(self._model.tokenize(value.encode("utf-8")))

        token_count += 1
        logger.debug("get_token_count, token_count=%s", token_count)

        return token_count

    async def generate_answer(
        self, messages: List[dict[str, str]], max_tokens: int
    ) -> str:
        """Answer using provided message list"""
        logger.debug(
            "generate_answer, self=%s, messages=%s, max_tokens=%s",
            self,
            messages,
            max_tokens,
        )

        llm_messages: list[dict[str, str]] = []

        if (
            self._configuration.prompt_system is not None
            and self._configuration.prompt_system != ""
        ):
            llm_messages += [
                {
                    "role": "system",
                    "content": self._configuration.prompt_system,
                }
            ]

        llm_messages += messages
        remaining_context_length: int = (
            self._configuration.context_length - self.get_token_count(llm_messages)
        )

        logger.debug(
            "generate_answer, remaining_context_length=%s, max_tokens=%s",
            remaining_context_length,
            max_tokens,
        )

        if remaining_context_length < 0:
            raise ValueError("Provided messages exceed the maximum context length.")

        if max_tokens > remaining_context_length:
            max_tokens = remaining_context_length

        completion: ChatCompletion = self._model.create_chat_completion(
            messages,
            top_k=self._configuration.top_k,
            top_p=self._configuration.top_p,
            temperature=self._configuration.temperature,
            repeat_penalty=self._configuration.repeat_penalty,
            max_tokens=max_tokens,
        )

        logger.debug("generate_answer, completion=%s", completion)

        return completion["choices"][0]["message"]["content"]
