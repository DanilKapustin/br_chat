from logging import getLogger

from llama_cpp import Llama

from chatbot.service.model import BaseModel
from .configuration import Configuration

SYSTEM_TOKEN = 1587
USER_TOKEN = 2188
BOT_TOKEN = 12435
LINEBREAK_TOKEN = 13
ROLE_TOKENS = {"user": USER_TOKEN, "assistant": BOT_TOKEN, "system": SYSTEM_TOKEN}

logger = getLogger(__name__)


class Model(BaseModel):
    """Saiga-2 LLM (llama.cpp)"""

    IS_LOCAL: bool = True

    def __init__(self, configuration: Configuration):
        """Constructor"""
        super().__init__(configuration)

        logger.info("__init__, loading model")

        self._configuration: Configuration = configuration
        self._model: Llama = Llama(
            model_path=configuration.path,
            n_ctx=configuration.context_length,
            n_parts=1,
            n_threads=configuration.threads,
            n_gpu_layers=configuration.gpu_layers,
            n_batch=512,
        )

    def __del__(self):
        """Destructor"""
        logger.info("__del__, unloading model")
        del self._model

    def _get_message_tokens(self, role: str, content: str) -> list[int]:
        """Get tokens for message"""
        message_tokens: list[int] = self._model.tokenize(content.encode("utf-8"))
        message_tokens.insert(1, ROLE_TOKENS[role])
        message_tokens.insert(2, LINEBREAK_TOKEN)
        message_tokens.append(self._model.token_eos())

        return message_tokens

    def get_token_count(self, messages: list[dict[str, str]]) -> int:
        """Return the number of tokens used by a list of messages."""
        logger.debug("get_token_count, self=%s, messages=%s", self, len(messages))

        token_count: int = 0

        for message in messages:
            token_count += len(
                self._get_message_tokens(
                    role=message.get("role"), content=message.get("content")
                )
            )

        token_count += 3  # BOS, BOT, LINEBREAK
        logger.debug("get_token_count, token_count=%s", token_count)

        return token_count

    async def generate_answer(
        self, messages: list[dict[str, str]], max_tokens: int
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

        tokens: list[int] = []

        for message in llm_messages:
            tokens += self._get_message_tokens(
                role=message.get("role"), content=message.get("content")
            )

        tokens += [self._model.token_bos(), BOT_TOKEN, LINEBREAK_TOKEN]
        generator = self._model.generate(
            tokens,
            top_k=self._configuration.top_k,
            top_p=self._configuration.top_p,
            temp=self._configuration.temperature,
            repeat_penalty=self._configuration.repeat_penalty,
        )

        response_message: str = ""
        token_counter = 0

        for token in generator:
            decoded: str = self._model.detokenize([token]).decode(
                "utf-8", errors="ignore"
            )
            response_message += decoded
            token_counter += 1

            if token == self._model.token_eos() or token_counter >= max_tokens:
                break

        return response_message
