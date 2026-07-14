"""Shared base utilities for Helix agent scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from memory_manager import MemoryManager, get_memory_manager
from model_backend import ModelBackend, get_model_backend
from rag.retriever import Retriever


class Agent:
    """Base class for local Helix agents."""

    def __init__(
        self,
        name: str,
        memory_manager: Optional[MemoryManager] = None,
        backend: Optional[ModelBackend] = None,
        retriever: Optional[Retriever] = None,
    ) -> None:
        self.name = name
        self.agent_dir = Path(__file__).parent
        self.command_center_dir = self.agent_dir.parent
        self.project_root = self.command_center_dir.parent
        self.memory_manager = memory_manager or get_memory_manager()
        self.backend = backend or get_model_backend()
        self.retriever = retriever or Retriever()

    def remember(self, prompt: str, response: str) -> None:
        """Record a successful agent interaction."""
        self.memory_manager.add_accomplishment(
            self.name.upper(),
            f"Processed: {prompt[:50]}...",
            {"full_prompt": prompt, "response_preview": response[:100]},
        )

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """Retrieve relevant context chunks for a query and join them into
        a single string suitable for prompt injection.

        Args:
            query: The natural-language query to search memory/knowledge for.
            top_k: Maximum number of chunks to retrieve.

        Returns:
            A newline-joined string of retrieved context chunks. Returns an
            empty string if retrieval fails or nothing is found — this method
            must never raise, since context retrieval is an enhancement, not
            a hard dependency for an agent to function.
        """
        try:
            chunks = self.retriever.retrieve(query, top_k=top_k)
            return "\n".join(chunks)
        except Exception:
            return ""

    def index_memory(self, source_id: str, text: str) -> int:
        """Index a piece of text into the shared vector store under source_id.

        Args:
            source_id: Identifier for what this text represents (e.g.,
                agent name + timestamp, or a memory file name).
            text: The raw text content to index.

        Returns:
            Number of chunks indexed. Returns 0 if indexing fails — this
            method must never raise.
        """
        try:
            return self.retriever.index_text(source_id, text)
        except Exception:
            return 0
