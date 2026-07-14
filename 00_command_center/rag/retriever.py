"""High-level RAG interface composing chunking, embedding, and vector storage."""

from __future__ import annotations

from rag.embedder import Embedder, OllamaEmbedder
from rag.chunker import chunk_text
from rag.vector_store import VectorStore


class Retriever:
    """Indexes text and retrieves relevant chunks for RAG queries.

    All dependencies are injectable for testing.  When no arguments are
    provided the class wires up ``OllamaEmbedder`` and ``VectorStore`` with
    their default settings.

    Args:
        embedder: Embedding backend.  Defaults to ``OllamaEmbedder()``.
        store: Vector store backend.  Defaults to ``VectorStore()``.
    """

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
    ) -> None:
        self.embedder = embedder or OllamaEmbedder()
        self.store = store or VectorStore()

    def index_text(self, source_id: str, text: str) -> int:
        """Chunk, embed, and store *text* under the given *source_id*.

        Each chunk is assigned a deterministic id of the form
        ``"{source_id}_chunk{i}"`` and tagged with source metadata.

        Args:
            source_id: Identifier for the originating document.
            text: Raw text content to index.

        Returns:
            The number of chunks that were indexed.
        """
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_id}_chunk{i}"
            embedding = self.embedder.embed(chunk)
            self.store.add(
                chunk_id=chunk_id,
                text=chunk,
                embedding=embedding,
                metadata={"source": source_id, "chunk_index": i},
            )

        return len(chunks)

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Return the most relevant text chunks for *query*.

        Args:
            query: Natural-language query string.
            top_k: Maximum number of chunks to return.

        Returns:
            A flat list of retrieved text strings, ordered by relevance.
        """
        query_embedding = self.embedder.embed(query)
        results = self.store.query(query_embedding=query_embedding, top_k=top_k)
        return [result["text"] for result in results]


_retriever_instance = None

def get_retriever() -> Retriever:
    """Get or create the shared Retriever singleton instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance
