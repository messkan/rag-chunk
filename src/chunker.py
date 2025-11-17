"""Chunking strategies."""

from typing import Dict, List

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None


def tokenize(
    text: str, use_tiktoken: bool = False, model: str = "gpt-3.5-turbo"
) -> List[str]:
    """Tokenize text using whitespace or tiktoken.

    Args:
        text: Text to tokenize
        use_tiktoken: If True, use tiktoken for token-based splitting
        model: Model name for tiktoken encoding (default: gpt-3.5-turbo)

    Returns:
        List of tokens (strings for whitespace, or token strings for tiktoken)
    """
    if use_tiktoken:
        if not TIKTOKEN_AVAILABLE:
            raise ImportError(
                "tiktoken is not installed. Install it with: pip install rag-chunk[tiktoken]"
            )
        encoding = tiktoken.encoding_for_model(model)
        token_ids = encoding.encode(text)
        # Return token strings for consistency
        return [encoding.decode([tid]) for tid in token_ids]
    return [t for t in text.split() if t]


def count_tokens(
    text: str, use_tiktoken: bool = False, model: str = "gpt-3.5-turbo"
) -> int:
    """Count tokens in text.

    Args:
        text: Text to count tokens in
        use_tiktoken: If True, use tiktoken for accurate token counting
        model: Model name for tiktoken encoding

    Returns:
        Number of tokens
    """
    if use_tiktoken:
        if not TIKTOKEN_AVAILABLE:
            raise ImportError(
                "tiktoken is not installed. Install it with: pip install rag-chunk[tiktoken]"
            )
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    return len([t for t in text.split() if t])


def fixed_size_chunks(
    text: str, chunk_size: int, use_tiktoken: bool = False, model: str = "gpt-3.5-turbo"
) -> List[Dict]:
    """Split text into fixed-size chunks.

    Args:
        text: Text to chunk
        chunk_size: Number of tokens per chunk
        use_tiktoken: If True, use tiktoken for token-based chunking
        model: Model name for tiktoken encoding
    Returns:
        List of chunk dictionaries with 'id' and 'text' keys
    """
    tokens = tokenize(text, use_tiktoken=use_tiktoken, model=model)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        part = tokens[i : i + chunk_size]
        chunks.append(
            {
                "id": len(chunks),
                "text": "".join(part) if use_tiktoken else " ".join(part),
            }
        )
    return chunks


def sliding_window_chunks(
    text: str,
    chunk_size: int,
    overlap: int,
    use_tiktoken: bool = False,
    model: str = "gpt-3.5-turbo",
) -> List[Dict]:
    """Generate overlapping sliding window chunks.

    Args:
        text: Text to chunk
        chunk_size: Number of tokens per chunk
        overlap: Number of overlapping tokens between chunks
        use_tiktoken: If True, use tiktoken for token-based chunking
        model: Model name for tiktoken encoding
    Returns:
        List of chunk dictionaries with 'id' and 'text' keys
    """
    tokens = tokenize(text, use_tiktoken=use_tiktoken, model=model)
    step = max(1, chunk_size - overlap)
    chunks = []
    i = 0
    while i < len(tokens):
        part = tokens[i : i + chunk_size]
        if not part:
            break
        chunks.append(
            {
                "id": len(chunks),
                "text": "".join(part) if use_tiktoken else " ".join(part),
            }
        )
        i += step
    return chunks


def paragraph_chunks(text: str) -> List[Dict]:
    """Split by paragraph blank lines."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = [{"id": i, "text": p} for i, p in enumerate(paragraphs)]
    return chunks


STRATEGIES = {
    "fixed-size": lambda text, chunk_size=200, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo": fixed_size_chunks(
        text, chunk_size, use_tiktoken=use_tiktoken, model=model
    ),
    "sliding-window": lambda text, chunk_size=200, overlap=50, use_tiktoken=False, model="gpt-3.5-turbo": sliding_window_chunks(
        text, chunk_size, overlap, use_tiktoken=use_tiktoken, model=model
    ),
    "paragraph": lambda text, chunk_size=0, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo": paragraph_chunks(
        text
    ),
}
