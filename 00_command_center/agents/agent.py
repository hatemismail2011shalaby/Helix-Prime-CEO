"""Shared base utilities for Helix agent scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from memory_manager import MemoryManager, get_memory_manager
from model_backend import ModelBackend, get_model_backend


class Agent:
    """Base class for local Helix agents."""

    def __init__(
        self,
        name: str,
        memory_manager: Optional[MemoryManager] = None,
        backend: Optional[ModelBackend] = None,
    ) -> None:
        self.name = name
        self.agent_dir = Path(__file__).parent
        self.command_center_dir = self.agent_dir.parent
        self.project_root = self.command_center_dir.parent
        self.memory_manager = memory_manager or get_memory_manager()
        self.backend = backend or get_model_backend()

    def remember(self, prompt: str, response: str) -> None:
        """Record a successful agent interaction."""
        self.memory_manager.add_accomplishment(
            self.name.upper(),
            f"Processed: {prompt[:50]}...",
            {"full_prompt": prompt, "response_preview": response[:100]},
        )
