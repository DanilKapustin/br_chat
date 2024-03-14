from logging import getLogger
from os import environ
from typing import List

from sentence_transformers import SentenceTransformer

from .base import BaseEmbeddingModel

MODEL_PATH = environ.get("E5_MODEL_PATH", "/media/love/ml/multilingual-e5-base")
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "

logger = getLogger(__name__)


class E5(BaseEmbeddingModel):
    """E5 language embedding model"""

    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or load model"""
        if cls._model is None:
            logger.info("loading model")
            cls._model = SentenceTransformer(MODEL_PATH)

        return cls._model

    async def generate_embedding(self, is_query: bool, text: str) -> List[float]:
        """Generate embedding from text"""
        logger.debug(
            "generate_embedding, is_query=%s, text=%s", is_query, text[:20] + "..."
        )
        prefix: str = QUERY_PREFIX if is_query else PASSAGE_PREFIX
        input_text: str = prefix + text

        model: SentenceTransformer = E5.get_model()
        embedding: List[float] = model.encode(
            input_text, normalize_embeddings=True, show_progress_bar=False
        ).tolist()

        return embedding
