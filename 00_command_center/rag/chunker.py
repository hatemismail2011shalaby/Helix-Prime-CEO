"""Pure-function text chunking for RAG indexing.

Splits text into overlapping character-level chunks, breaking on whitespace
boundaries to avoid splitting mid-word.  No I/O, no external dependencies.
"""

from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """Split *text* into overlapping chunks of approximately *chunk_size* characters.

    Chunks break on whitespace boundaries wherever possible so that words are
    not split across chunks.  Each chunk (except the first) carries forward
    *overlap* characters from the end of the previous chunk to preserve local
    context across boundaries.

    Args:
        text: The source text to chunk.
        chunk_size: Target number of characters per chunk.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of chunk strings.  Text shorter than *chunk_size* is returned
        as a single-element list.
    """
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size ({chunk_size})"
        )

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            # Try to break on the last whitespace within the window.
            break_at = text.rfind(" ", start, end)
            if break_at > start:
                end = break_at

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Advance by chunk_size minus the overlap so context carries forward.
        start = max(start + 1, end - overlap) if end < len(text) else len(text)

    return chunks
