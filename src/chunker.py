"""Chunking strategies."""

from typing import Dict, List


def tokenize(text: str) -> List[str]:
    """Simple whitespace tokenization preserving order."""
    return [t for t in text.split() if t]


def fixed_size_chunks(text: str, chunk_size: int) -> List[Dict]:
    """Split text into fixed-size word chunks."""
    tokens = tokenize(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        part = tokens[i : i + chunk_size]
        chunks.append({"id": len(chunks), "text": " ".join(part)})
    return chunks


def sliding_window_chunks(text: str, chunk_size: int, overlap: int) -> List[Dict]:
    """Generate overlapping sliding window chunks."""
    tokens = tokenize(text)
    step = max(1, chunk_size - overlap)
    chunks = []
    i = 0
    while i < len(tokens):
        part = tokens[i : i + chunk_size]
        if not part:
            break
        chunks.append({"id": len(chunks), "text": " ".join(part)})
        i += step
    return chunks


def paragraph_chunks(text: str) -> List[Dict]:
    """Split by paragraph blank lines."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = [{"id": i, "text": p} for i, p in enumerate(paragraphs)]
    return chunks


STRATEGIES = {
    "fixed-size": lambda text, chunk_size=200, overlap=0: fixed_size_chunks(
        text, chunk_size
    ),
    "sliding-window": lambda text, chunk_size=200, overlap=50: sliding_window_chunks(
        text, chunk_size, overlap
    ),
    "paragraph": lambda text, chunk_size=0, overlap=0: paragraph_chunks(text),
}
