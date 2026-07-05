from __future__ import annotations

import os
import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Optional, Dict


def _normalize_roots(roots: Optional[Iterable[Path]]) -> List[Path]:
    if roots is None:
        return []

    normalized: List[Path] = []
    for root in roots:
        try:
            path = Path(root)
            if path.exists():
                normalized.append(path)
        except OSError:
            continue
    return normalized


def list_workspace_items(root: Path) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for path in sorted(root.iterdir()):
        if path.name.startswith("."):
            continue
        items.append({
            "name": path.name,
            "type": "folder" if path.is_dir() else "file",
            "path": str(path.relative_to(root)),
        })
    return items


def find_files_by_name(
    query: str,
    roots: Optional[Iterable[Path]] = None,
    max_results: int = 100,
) -> List[str]:
    """Find files whose names contain the query text."""
    query = query.strip().lower()
    if not query:
        return []

    roots_list = _normalize_roots(roots) or [Path.cwd()]
    matches: List[str] = []
    for root in roots_list:
        for path in root.rglob("*"):
            if len(matches) >= max_results:
                return matches
            if path.is_file() and query in path.name.lower():
                matches.append(str(path))
    return matches


def find_files_by_content(
    query: str,
    roots: Optional[Iterable[Path]] = None,
    file_patterns: Optional[List[str]] = None,
    max_results: int = 100,
) -> List[str]:
    """Search text inside files under the given root paths."""
    query = query.strip().lower()
    if not query:
        return []

    roots_list = _normalize_roots(roots) or [Path.cwd()]
    patterns = file_patterns or ["*.txt", "*.md", "*.py", "*.json", "*.yaml", "*.yml", "*.log"]
    matches: List[str] = []

    for root in roots_list:
        for path in root.rglob("*"):
            if len(matches) >= max_results:
                return matches
            if not path.is_file():
                continue
            if not any(fnmatch(path.name.lower(), pattern.lower()) for pattern in patterns):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            if query in text:
                matches.append(str(path))
    return matches


def read_file(path: Path, max_chars: int = 3000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n..."
        return text
    except OSError as exc:
        return f"Error: could not read file {path}: {exc}"


def normalize_query_to_paths(query: str) -> List[Path]:
    """Convert common path queries into Path objects."""
    roots: List[Path] = []
    if not query:
        return roots

    lower = query.lower()
    if "h:" in lower or "drive h" in lower:
        roots.append(Path("H:/"))
    if "workspace" in lower or "project" in lower or "root" in lower:
        roots.append(Path.cwd())
    return roots
