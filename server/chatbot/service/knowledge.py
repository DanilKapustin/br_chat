import re
import uuid
from typing import List, Optional
from uuid import UUID
from logging import getLogger
from xml.etree.ElementTree import Element

from fastapi_pagination import Page, Params

from chatbot.dto import KnowledgeResult, KnowledgeDocument
from chatbot.service.util import Language
from chatbot.service.embedding import factory, BaseEmbeddingModel
from chatbot.service.configuration import get_embedding_model
from chatbot.knowledge import DocumentCollection
from xml.etree import ElementTree
from collections import Counter, defaultdict

# TODO: make configurable, 2000 ~ 500-1000 tokens, 1000 ~ 250-500 tokens
CHUNK_SIZE_LIMIT_HEAD_TAIL = 201
CHUNK_SIZE_LIMIT = 512
CHUNK_GLUE = " "
NAMESPACE = UUID("d2f60322-9f0f-41b5-a36c-c3eab2e75b2e")

logger = getLogger(__name__)


async def _get_embedding(model_name: str, is_query: bool, text: str) -> List[float]:
    """Get embedding depending on model"""
    logger.debug(
        "_get_embedding, model_name=%s, is_query=%s, text=%s",
        model_name,
        is_query,
        text[:20] + "...",
    )

    model: BaseEmbeddingModel = factory.get(model_name)
    embedding: List[float] = await model.generate_embedding(is_query, text)
    logger.debug("_get_embedding, model=%s, embedding=%s", model, len(embedding))

    return embedding


async def get_list(
    collection: DocumentCollection, page: int, size: int
) -> Page[KnowledgeResult]:
    """Get list"""
    logger.debug("get_list, page=%s, size=%s", page, size)

    documents: List[KnowledgeResult] = await collection.search(
        offset=(page - 1) * size, limit=size
    )

    total_count: int = await collection.count()
    results: Page[KnowledgeResult] = Page.create(
        documents, Params(page=page, size=size), total=total_count
    )

    return results


async def get(
    collection: DocumentCollection, item_id: UUID
) -> Optional[KnowledgeResult]:
    """Get document from collection by id"""
    logger.debug("get, item_id=%s", item_id)

    result: Optional[KnowledgeResult] = None
    results: List[KnowledgeResult] = await collection.search([str(item_id)])

    if len(results) > 0:
        result = results[0]

    return result


async def delete(collection: DocumentCollection, item_id: UUID):
    """Delete document from collection by id"""
    logger.debug("delete, item_id=%s", item_id)
    await collection.delete([str(item_id)])


async def delete_all(collection: DocumentCollection):
    """Delete all documents from collection"""
    logger.debug("delete_all")
    await collection.drop()


def _traverse_xml(node: Element, depth: int, node_depths: defaultdict):
    node_depths[depth].append(node.tag)

    for child in node:
        _traverse_xml(child, depth + 1, node_depths)


def _find_repeating_xml_node(root: Element, min_repetitions: int = 10) -> Optional[str]:
    node_depths: defaultdict = defaultdict(list)
    _traverse_xml(root, 0, node_depths)

    for depth, tags in sorted(node_depths.items()):
        tag_counter: Counter = Counter(tags)

        for tag, count in tag_counter.most_common():
            if count >= min_repetitions:
                logger.debug("_find_repeating_xml_node, tag=%s, count=%s", tag, count)
                return tag

    return None


def _split_xml(document: KnowledgeDocument) -> list[str]:
    """Split document by XML tags"""
    logger.debug("_split_xml, document=%s", document)
    sentences: list[str] = []

    root: Element = ElementTree.fromstring(document.text)
    repeating_node: str = _find_repeating_xml_node(root)

    if repeating_node is None:
        raise ValueError("Cannot find a repeating node")

    # Find all nodes with the specified tag
    nodes = root.findall(".//" + repeating_node)

    # Splitting the file
    for idx, node in enumerate(nodes):
        node_string: str = ElementTree.tostring(node, encoding="unicode")
        sentences.append(node_string)
        # logger.debug("_split_xml, idx=%s, node=%s", idx, node_string)

    return sentences


def _split_long_sentences(sentences: list[str]) -> list[str]:
    """Split sentences that are longer than the limit"""
    logger.debug("_split_long_sentences, sentences=%s", len(sentences))
    result: list[str] = []

    for sentence in sentences:
        if len(sentence) <= CHUNK_SIZE_LIMIT:
            result.append(sentence)
        else:
            chunks: list[str] = sentence.split("\n")
            current_chunk: list[str] = []
            current_chunk_size: int = 0

            for chunk in chunks:
                if current_chunk_size + len(chunk) >= CHUNK_SIZE_LIMIT:
                    if len(current_chunk) > 0:
                        result.append("\n".join(current_chunk))

                    current_chunk = []
                    current_chunk_size = 0

                current_chunk.append(chunk)
                current_chunk_size += len(chunk)

            if len(current_chunk) > 0:
                result.append(" ".join(current_chunk))

    return result


def _split_sentences(document: KnowledgeDocument) -> list[str]:
    """Split document by sentences"""
    logger.debug("_split_sentences, document=%s", document)
    sentences: list[str]

    match document.type:
        case "csv":
            sentences = list(
                filter(lambda line: len(line.strip()) > 0, document.text.split("\n"))
            )

        case "xml":
            sentences = _split_xml(document)

        case _:
            language: Language = Language()
            sentences = language.split_sentences(document.text)
            sentences = _split_long_sentences(sentences)

    return sentences


def _clear_text(text: str) -> str:
    """Clear text"""
    logger.debug("_clear_text, text=%s", len(text))

    text = re.sub(r"\t", "    ", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\r", "\n", text)
    text = re.sub(" +\n", "\n", text)
    text = re.sub(r"\n+", "\n", text)

    return text


def _prepare_and_split(document: KnowledgeDocument) -> list[str]:
    """Prepare text - clear it, and split by chunks"""
    logger.debug("_prepare_and_split, document=%s", document)

    text: str = document.text

    if len(text) <= CHUNK_SIZE_LIMIT:
        return [text]

    sentences: list[str] = _split_sentences(document)
    chunks: list[str] = []
    chunk_size: int = 0
    current_chunk: list[str] = []

    logger.debug("_prepare_and_split, sentences=%s", len(sentences))

    for sentence in sentences:
        # adding a chunk would exceed the limit
        if chunk_size + len(sentence) >= CHUNK_SIZE_LIMIT:
            if len(current_chunk) > 0:
                chunks.append(CHUNK_GLUE.join(current_chunk))

            current_chunk = []
            chunk_size = 0

        current_chunk.append(sentence)
        chunk_size += len(sentence)

    if len(current_chunk) > 0:
        chunks.append(CHUNK_GLUE.join(current_chunk))

    return chunks

def chunks_with_overlays(prev: str, cur: str, _next: str) -> str:
    """Helps to add CHUNK_SIZE_LIMIT_HEAD_TAIL characters to a chunk from the previous and next chunk."""

    def get_overlay(sentences: list[str], _reverse: bool = False) -> str:
        """
        Helper function to get the overlay part from a list of sentences.
        """
        overlay = []
        total_length = 0

        sentences_iter = reversed(sentences) if _reverse else sentences

        for sentence in sentences_iter:
            if sentence != '#_#_#' and total_length + len(sentence) <= CHUNK_SIZE_LIMIT_HEAD_TAIL:
                total_length += len(sentence)
                overlay.append(sentence)

        return '\n'.join(reversed(overlay) if _reverse else overlay)

    temp_head = _next.split('\n')
    temp_tail = prev.split('\n')

    if prev == cur:  # situation when first chunk
        temp_tail = ['#_#_#']
    if _next == cur:  # situation when last chunk
        temp_head = ['#_#_#']

    start = get_overlay(temp_tail, _reverse=True)
    end = get_overlay(temp_head)

    chunk = f"{start} {cur} {end}"

    return chunk

def generate_id(
    source_id: str, url: str, title: str, subtitle: str, chunk: int
) -> UUID:
    """Generate id from url and chunk"""
    return uuid.uuid3(NAMESPACE, f"{source_id}/{url}/{title}/{subtitle}/{chunk}")


async def create(
    source_id: str,
    source_title: str,
    document: KnowledgeDocument,
    can_split: bool = True,
):
    """Create document in collection"""
    logger.debug(
        "create, source_id=%s, source_title=%s, document=%s, can_split=%s",
        source_id,
        source_title,
        document,
        can_split,
    )

    collection: DocumentCollection = DocumentCollection()
    document.text = _clear_text(document.text)
    chunks: List[str] = [document.text]

    if can_split:
        chunks = _prepare_and_split(document)

    logger.debug("create, got chunks=%s", len(chunks))
    model: str = await get_embedding_model()

    for i, chunk in enumerate(chunks):
        if len(chunks) > 2:
            prev_chunk = chunks[i - 1] if i > 0 else chunk
            next_chunk = chunks[i + 1] if i < len(chunks) - 1 else chunk
            chunk = chunks_with_overlays(prev_chunk, chunk, next_chunk)

        logger.debug(
            "create, source_id=%s, i=%s, chunk=%s", source_id, i, chunk[:20] + "..."
        )

        metadata: dict[str, str] = dict(
            source_id=source_id,
            source_title=source_title,
            chunk=i + 1,
            total_chunks=len(chunks),
        )

        document_id: UUID = generate_id(
            source_id, document.url, document.title, document.subtitle, i
        )

        # metadata values cannot be None
        metadata |= {
            k: v for k, v in document.dict(exclude={"text"}).items() if v is not None
        }

        await collection.upsert(
            ids=[str(document_id)],
            embeddings=[await _get_embedding(model, False, chunk)],
            metadatas=[metadata],
            documents=[chunk],
        )


async def search(
    query: str, limit: int, metadata_filter: Optional[dict] = None
) -> List[KnowledgeResult]:
    """Search documents in collection"""
    logger.debug(
        "search, query=%s, limit=%s, metadata_filter=%s", query, limit, metadata_filter
    )

    collection: DocumentCollection = DocumentCollection()
    model: str = await get_embedding_model()

    embedding: List[float] = await _get_embedding(model, True, query)
    result: List[KnowledgeResult] = await collection.query_embeddings(
        embedding, limit, metadata_filter
    )
    logger.debug("search, found items=%s", len(result))

    return result
