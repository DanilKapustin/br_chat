from chatbot.dto import ToolConfiguration


class Configuration(ToolConfiguration):
    """Question answering configuration"""

    max_results: int = 3
    max_tokens: int = 1000
    prompt_answer: str
    prompt_compress_question: str
    answer_negative: str
