from typing import Optional
from pydantic import BaseModel


class KnowledgeResult(BaseModel):
    """Knowledge result DTO"""

    id: str
    source_id: str
    source_title: str
    title: str
    subtitle: Optional[str]
    url: Optional[str]
    chunk: Optional[int]
    total_chunks: Optional[int]
    text: Optional[str]

    def __repr__(self) -> str:
        return f"KnowledgeResult(id={self.id}, source_id={self.source_id}, title={self.title})"

    def __str__(self) -> str:
        return self.__repr__()


class KnowledgeDocument(BaseModel):
    """KnowledgeDocument DTO"""

    title: str
    type: str
    subtitle: Optional[str]
    url: Optional[str]
    text: str

    def __repr__(self) -> str:
        return f"KnowledgeDocument(title={self.title}, type={self.type}, subtitle={self.subtitle}, url={self.url})"

    def __str__(self) -> str:
        return self.__repr__()
