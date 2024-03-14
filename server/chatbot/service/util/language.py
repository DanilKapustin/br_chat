from logging import getLogger
from typing import List, Optional
from spacy import load
from spacy.language import Language as SpacyLanguage, Doc as SpacyDoc
import spacy_fastlang

LANGUAGE_MODELS = {
    "en": "en_core_web_sm",
    "ru": "ru_core_news_sm"
}

# TODO: configure default language
DEFAULT_LANGUAGE = "en"

logger = getLogger(__name__)


class Language:
    """Language utils using Spacy"""
    _models: dict[str, SpacyLanguage] = {}

    @classmethod
    def get_model(cls, language: Optional[str] = None) -> SpacyLanguage:
        """Get model by language"""
        if language is None:
            language = DEFAULT_LANGUAGE

        if language not in cls._models or cls._models[language] is None:
            logger.info("loading model for %s", language)
            cls._models[language] = load(LANGUAGE_MODELS[language])
            cls._models[language].add_pipe("language_detector")

        return cls._models[language]

    def _get_model_by_text(self, text: str) -> SpacyLanguage:
        """Get model by text"""
        language: str = self.detect_language(text)

        if language == DEFAULT_LANGUAGE or language not in LANGUAGE_MODELS:
            return Language.get_model()

        return Language.get_model(language)

    def detect_language(self, text: str) -> str:
        """Get language by text sample"""
        model: SpacyLanguage = Language.get_model()
        document: SpacyDoc = model(text)
        language: str = document._.language

        return language

    def split_sentences(self, text: str) -> List[str]:
        """Split text by sentences"""
        model: SpacyLanguage = self._get_model_by_text(text)
        return [sentence.text for sentence in model(text).sents]
