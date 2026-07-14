import os
from abc import ABC, abstractmethod

import ollama


class Embedder(ABC):
    """Abstract base class for RAG embedders."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Embed a single text string and return its dense vector representation.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        ...


class OllamaEmbedder(Embedder):
    """Concrete embedder using a local Ollama embedding model."""

    def __init__(self, model: str = "nomic-embed-text") -> None:
        self._model = os.getenv("HELIX_EMBED_MODEL", model)

    def embed(self, text: str) -> list[float]:
        """Embed text via Ollama and return the embedding vector.

        Raises:
            RuntimeError: If the Ollama call fails for any reason.
        """
        try:
            result = ollama.embeddings(model=self._model, prompt=text)
            return result["embedding"]
        except Exception as e:
            raise RuntimeError(f"Failed to embed text with model '{self._model}': {e}") from e


def embed_batch(embedder: Embedder, texts: list[str]) -> list[list[float]]:
    """Embed a list of strings sequentially.

    Args:
        embedder: An Embedder instance.
        texts: List of text strings to embed.

    Returns:
        A list of embedding vectors, one per input text, in the same order.
    """
    return [embedder.embed(text) for text in texts]
