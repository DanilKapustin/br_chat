from logging import getLogger
from typing import List, Optional, AsyncIterator

from chromadb import Collection, ClientAPI
from chromadb.api.types import (
    OneOrMany,
    Embedding,
    Metadata,
    Document,
    ID,
    IDs,
    QueryResult,
    GetResult,
)

from chatbot.dto.knowledge import KnowledgeResult
from chatbot.util.aio import make_async
from chatbot.util.singleton import singleton
from .connection import Connection

COLLECTION_NAME = "stack_document_collection"
VECTOR_DIMENSIONS = 768
COSINE_DISTANCE_LIMIT = 0.25

logger = getLogger(__name__)


# TODO: fix async, as @make_async wraps everything in new event loop
@singleton
class DocumentCollection:
    """Chroma document collection"""

    def __init__(self):
        """Constructor"""
        logger.debug("__init__")

        self.client: Optional[ClientAPI] = Connection().client
        self.collection: Optional[Collection] = None
        self.create()

    def create(self):
        """Create collection"""
        logger.debug("create")

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    @make_async
    def query_embeddings(
        self,
        query_embeddings: Optional[OneOrMany[Embedding]],
        n_results: int,
        metadata_filter: Optional[dict] = None,
    ) -> List[KnowledgeResult]:
        """Query collection with embeddings"""
        logger.debug(
            "query_embeddings, query_embeddings=%s, n_results=%s, metadata_filter=%s",
            len(query_embeddings),
            n_results,
            metadata_filter,
        )
        query_result: QueryResult = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=metadata_filter,
        )
        logger.debug("query_embeddings, query_result=%s", query_result)
        result: List[KnowledgeResult] = []
        logger.debug("query_embeddings, query_result.ids=%s", query_result["ids"][0])

        for i in range(len(query_result["ids"][0])):
            distance: float = query_result["distances"][0][i]

            if distance > COSINE_DISTANCE_LIMIT:
                continue

            metadata: Metadata = query_result["metadatas"][0][i]
            knowledge_result: KnowledgeResult = KnowledgeResult(
                id=query_result["ids"][0][i],
                text=query_result["documents"][0][i],
                **metadata
            )

            result.append(knowledge_result)

        return result

    @make_async
    def delete(self, ids: IDs):
        """Delete document"""
        logger.debug("delete, ids=%s", ids)
        return self.collection.delete(ids)

    @make_async
    def upsert(
        self,
        ids: OneOrMany[ID],
        embeddings: Optional[OneOrMany[Embedding]] = None,
        metadatas: Optional[OneOrMany[Metadata]] = None,
        documents: Optional[OneOrMany[Document]] = None,
    ):
        """Insert/update document"""
        logger.debug(
            "upsert, ids=%s, embeddings=%s, metadatas=%s, documents=%s",
            ids,
            len(embeddings),
            len(metadatas),
            len(documents),
        )
        return self.collection.upsert(ids, embeddings, metadatas, documents)

    @make_async
    def search(
        self,
        ids: Optional[OneOrMany[ID]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[KnowledgeResult]:
        """Search collection"""
        logger.debug("search, ids=%s, limit=%s, offset=%s", ids, limit, offset)

        search_result: GetResult = self.collection.get(
            ids=ids, limit=limit, offset=offset, include=["documents", "metadatas"]
        )
        result: List[KnowledgeResult] = []

        for i in range(len(search_result["ids"])):
            metadata: Metadata = search_result["metadatas"][i]
            logger.debug("search, i=%s, metadata=%s", i, metadata)

            knowledge_result: KnowledgeResult = KnowledgeResult(
                id=search_result["ids"][i],
                text=search_result["documents"][i],
                **metadata
            )

            result.append(knowledge_result)

        return result

    @make_async
    def count(self) -> int:
        """Get document count"""
        logger.debug("count")
        return self.collection.count()

    @make_async
    def drop(self):
        """Delete collection"""
        logger.debug("drop")

        self.client.delete_collection(COLLECTION_NAME)
        self.create()


async def get_collection() -> AsyncIterator[DocumentCollection]:
    """Get collection"""
    yield DocumentCollection()
