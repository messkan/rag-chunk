"""Chunking strategies."""

from typing import Dict, List

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    RecursiveCharacterTextSplitter = None


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


def recursive_character_chunks(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50,
    use_tiktoken: bool = False,
    model: str = "gpt-3.5-turbo",
) -> List[Dict]:
    """Split text using LangChain's RecursiveCharacterTextSplitter.

    Recursively splits by paragraphs, sentences, then words for semantic coherence.

    Args:
        text: Text to chunk
        chunk_size: Target size per chunk (words or tokens)
        overlap: Overlap between chunks
        use_tiktoken: If True, use tiktoken for token-based chunking
        model: Model name for tiktoken encoding

    Returns:
        List of chunk dictionaries with 'id' and 'text' keys
    """
    if not LANGCHAIN_AVAILABLE:
        raise ImportError(
            "LangChain is required for recursive-character strategy. "
            "Install with: pip install rag-chunk[langchain]"
        )

    if use_tiktoken:
        if not TIKTOKEN_AVAILABLE:
            raise ImportError(
                "tiktoken is required for token-based chunking. "
                "Install with: pip install rag-chunk[tiktoken]"
            )
        enc = tiktoken.encoding_for_model(model)
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name=enc.name,
            chunk_size=chunk_size,
            chunk_overlap=overlap,
        )
    else:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    texts = splitter.split_text(text)
    return [{"id": i, "text": t} for i, t in enumerate(texts)]


def header_aware_chunks(
    text: str,
    chunk_size: int = 200,
    overlap: int = 0,
    use_tiktoken: bool = False,
    model: str = "gpt-3.5-turbo",
) -> List[Dict]:
    """Split text by markdown headers while respecting chunk size limits.

    Preserves document structure by splitting at header boundaries.
    If a section exceeds chunk_size, it's further split using fixed-size strategy.

    Args:
        text: Text to chunk (should be markdown)
        chunk_size: Maximum tokens per chunk
        overlap: Overlap between chunks when splitting large sections
        use_tiktoken: If True, use tiktoken for token-based chunking
        model: Model name for tiktoken encoding

    Returns:
        List of chunk dictionaries with 'id', 'text', and 'metadata' keys
    """
    import re

    # Split by markdown headers (# to ####)
    header_pattern = r"^(#{1,4})\s+(.+)$"
    lines = text.split("\n")
    sections = []
    current_section = {"header": None, "level": 0, "content": []}

    for line in lines:
        match = re.match(header_pattern, line)
        if match:
            # Save previous section
            if current_section["content"]:
                sections.append(current_section)
            # Start new section
            level = len(match.group(1))
            header_text = match.group(2).strip()
            current_section = {
                "header": header_text,
                "level": level,
                "content": [line],
            }
        else:
            current_section["content"].append(line)

    # Add last section
    if current_section["content"]:
        sections.append(current_section)

    # Convert sections to chunks
    chunks = []
    for section in sections:
        section_text = "\n".join(section["content"]).strip()
        if not section_text:
            continue

        token_count = count_tokens(section_text, use_tiktoken, model)

        # If section fits in chunk_size, keep it as one chunk
        if token_count <= chunk_size:
            chunks.append(
                {
                    "id": len(chunks),
                    "text": section_text,
                    "metadata": {
                        "header": section["header"],
                        "level": section["level"],
                    },
                }
            )
        else:
            # Section too large, split it using sliding window
            sub_chunks = sliding_window_chunks(
                section_text, chunk_size, overlap, use_tiktoken, model
            )
            for i, sub_chunk in enumerate(sub_chunks):
                chunks.append(
                    {
                        "id": len(chunks),
                        "text": sub_chunk["text"],
                        "metadata": {
                            "header": section["header"],
                            "level": section["level"],
                            "sub_chunk": i,
                        },
                    }
                )

    return chunks


def semantic_chunks(
    text: str,
    chunk_size: int = 200,
    overlap: int = 0,
    use_tiktoken: bool = False,
    model: str = "gpt-3.5-turbo",
    threshold: float = 0.5,
) -> List[Dict]:
    """Split text at semantic boundaries using sentence embeddings.

    Groups consecutive sentences with high semantic similarity together.
    Splits when similarity drops below threshold or chunk_size is reached.

    Args:
        text: Text to chunk
        chunk_size: Maximum tokens per chunk
        overlap: Number of sentences to overlap between chunks
        use_tiktoken: If True, use tiktoken for token counting
        model: Model name for tiktoken encoding
        threshold: Cosine similarity threshold for grouping sentences (0-1)

    Returns:
        List of chunk dictionaries with 'id' and 'text' keys
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
    except ImportError:
        raise ImportError(
            "sentence-transformers is required for semantic chunking. "
            "Install with: pip install rag-chunk[semantic]"
        )

    # Split into sentences
    import re

    sentence_endings = r"[.!?]+[\s\n]+"
    sentences = [s.strip() for s in re.split(sentence_endings, text) if s.strip()]

    if len(sentences) <= 1:
        return [{"id": 0, "text": text}]

    # Load embedding model (cached after first load)
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(sentences)

    # Group sentences by semantic similarity
    chunks = []
    current_chunk = [sentences[0]]
    current_tokens = count_tokens(sentences[0], use_tiktoken, model)

    for i in range(1, len(sentences)):
        sentence = sentences[i]
        sentence_tokens = count_tokens(sentence, use_tiktoken, model)

        # Calculate similarity with last sentence in current chunk
        similarity = np.dot(embeddings[i], embeddings[i - 1]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i - 1])
        )

        # Check if we should start a new chunk
        should_split = (
            similarity < threshold  # Semantic boundary
            or current_tokens + sentence_tokens > chunk_size  # Size limit
        )

        if should_split and current_chunk:
            chunk_text = ". ".join(current_chunk) + "."
            chunks.append({"id": len(chunks), "text": chunk_text})
            # Handle overlap
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:]
                current_tokens = sum(
                    count_tokens(s, use_tiktoken, model) for s in current_chunk
                )
            else:
                current_chunk = []
                current_tokens = 0

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    # Add final chunk
    if current_chunk:
        chunk_text = ". ".join(current_chunk) + "."
        chunks.append({"id": len(chunks), "text": chunk_text})

    return chunks


STRATEGIES = {
    "fixed-size": (
        lambda text, chunk_size=200, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo":
            fixed_size_chunks(
                text,
                chunk_size,
                use_tiktoken=use_tiktoken,
                model=model,
            )
    ),
    "sliding-window": (
        lambda text, chunk_size=200, overlap=50, use_tiktoken=False, model="gpt-3.5-turbo":
            sliding_window_chunks(
                text,
                chunk_size,
                overlap,
                use_tiktoken=use_tiktoken,
                model=model,
            )
    ),
    "paragraph": (
        lambda text, chunk_size=0, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo":
            paragraph_chunks(text)
    ),
    "recursive-character": (
        lambda text, chunk_size=200, overlap=50, use_tiktoken=False, model="gpt-3.5-turbo":
            recursive_character_chunks(
                text,
                chunk_size,
                overlap,
                use_tiktoken=use_tiktoken,
                model=model,
            )
    ),
    "header": (
        lambda text, chunk_size=200, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo":
            header_aware_chunks(
                text,
                chunk_size,
                overlap,
                use_tiktoken=use_tiktoken,
                model=model,
            )
    ),
    "semantic": (
        lambda text, chunk_size=200, overlap=1, use_tiktoken=False, model="gpt-3.5-turbo":
            semantic_chunks(
                text,
                chunk_size,
                overlap,
                use_tiktoken=use_tiktoken,
                model=model,
            )
    ),
}
