"""ChromaDB-backed vector store for storing and querying embedded chunks."""

from __future__ import annotations

import chromadb


class VectorStore:
    """Thin wrapper around a ChromaDB persistent collection.

    Args:
        persist_dir: Filesystem path for ChromaDB's on-disk storage.
        collection_name: Name of the ChromaDB collection to use.
    """

    def __init__(
        self,
        persist_dir: str = "06_memory/vector_store",
        collection_name: str = "helix_memory",
    ) -> None:
        try:
            self._client = chromadb.PersistentClient(path=persist_dir)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to create ChromaDB PersistentClient at '{persist_dir}': {exc}"
            ) from exc

        try:
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to get or create collection '{collection_name}': {exc}"
            ) from exc

    def add(
        self,
        chunk_id: str,
        text: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        """Upsert a single chunk into the collection.

        Uses ``upsert`` so that re-indexing the same *chunk_id* updates the
        existing record rather than creating a duplicate.

        Args:
            chunk_id: Unique identifier for the chunk.
            text: The raw text content of the chunk.
            embedding: Vector embedding for the chunk.
            metadata: Optional metadata dict stored alongside the chunk.
        """
        try:
            self._collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}],
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to upsert chunk '{chunk_id}': {exc}"
            ) from exc

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        """Find the most similar chunks for the given query embedding.

        Args:
            query_embedding: Vector embedding of the query.
            top_k: Maximum number of results to return.

        Returns:
            A list of dicts, each containing ``"text"``, ``"metadata"``, and
            ``"distance"`` keys.  Returns an empty list when the collection has
            no entries.
        """
        if self._collection.count() == 0:
            return []

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to query collection: {exc}"
            ) from exc

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not documents or not documents[0]:
            return []

        output: list[dict] = []
        for i, doc in enumerate(documents[0]):
            output.append({
                "text": doc,
                "metadata": metadatas[0][i] if metadatas else {},
                "distance": distances[0][i] if distances else None,
            })

        return output
