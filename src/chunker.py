"""Chunking strategies."""

import re
from typing import Dict, List, Optional, Tuple

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

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None
    np = None


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


def _split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic punctuation."""
    # Simple sentence splitter - splits on . ! ? followed by space/newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def _extract_markdown_sections(text: str) -> List[Tuple[str, str, int]]:
    """Extract markdown sections based on headers.

    Returns:
        List of (header_text, content, level) tuples where level is 1-6 for h1-h6
    """
    sections = []
    lines = text.split('\n')
    current_header = ""
    current_content = []
    current_level = 0

    for line in lines:
        # Check for ATX-style headers (# Header)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            # Save previous section
            if current_content:
                sections.append((
                    current_header,
                    '\n'.join(current_content).strip(),
                    current_level
                ))
            # Start new section
            current_level = len(header_match.group(1))
            current_header = header_match.group(2).strip()
            current_content = []
        else:
            current_content.append(line)

    # Add final section
    if current_content:
        sections.append((
            current_header,
            '\n'.join(current_content).strip(),
            current_level
        ))

    return sections


def hierarchical_chunk(
    text: str,
    levels: Optional[List[str]] = None,
    use_tiktoken: bool = False,
    model: str = "gpt-3.5-turbo",
    source_path: str = "",
) -> List[Dict]:
    """Build multi-level chunk hierarchies.

    Splits text hierarchically: section → paragraph → sentence

    Args:
        text: Text to chunk
        levels: List of levels to split by. Options: 'section', 'paragraph', 'sentence'
               Default: ['section', 'paragraph']
        use_tiktoken: If True, use tiktoken for token counting
        model: Model name for tiktoken encoding
        source_path: Optional source file path for metadata

    Returns:
        List of chunk dictionaries with metadata:
        - id: unique chunk identifier
        - text: chunk text
        - parent_id: parent chunk id (None for top level)
        - level: hierarchy level name
        - start_char: start position in original text
        - end_char: end position in original text
        - token_count: number of tokens
        - source_path: source file path
    """
    if levels is None:
        levels = ['section', 'paragraph']

    chunks = []
    chunk_id = 0

    # Level 1: Try to split by sections (markdown headers)
    if 'section' in levels:
        sections = _extract_markdown_sections(text)

        # If no sections found, fallback to treating entire text as one section
        if not sections or (len(sections) == 1 and sections[0][0] == "" and sections[0][2] == 0):
            sections = [("", text, 0)]

        for header, content, level in sections:
            if not content.strip():
                continue

            # Find position in original text
            start_pos = text.find(content)
            end_pos = start_pos + len(content) if start_pos >= 0 else len(content)

            section_chunk = {
                "id": chunk_id,
                "text": content,
                "parent_id": None,
                "level": "section",
                "start_char": start_pos if start_pos >= 0 else 0,
                "end_char": end_pos,
                "token_count": count_tokens(content, use_tiktoken=use_tiktoken, model=model),
                "source_path": source_path,
                "header": header,
                "header_level": level,
            }
            chunks.append(section_chunk)
            section_parent_id = chunk_id
            chunk_id += 1

            # Level 2: Split sections into paragraphs
            if 'paragraph' in levels:
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

                for para in paragraphs:
                    para_start = text.find(para)
                    para_end = para_start + len(para) if para_start >= 0 else len(para)

                    para_chunk = {
                        "id": chunk_id,
                        "text": para,
                        "parent_id": section_parent_id,
                        "level": "paragraph",
                        "start_char": para_start if para_start >= 0 else 0,
                        "end_char": para_end,
                        "token_count": count_tokens(para, use_tiktoken=use_tiktoken, model=model),
                        "source_path": source_path,
                    }
                    chunks.append(para_chunk)
                    para_parent_id = chunk_id
                    chunk_id += 1

                    # Level 3: Split paragraphs into sentences
                    if 'sentence' in levels:
                        sentences = _split_into_sentences(para)

                        for sent in sentences:
                            sent_start = text.find(sent)
                            sent_end = sent_start + len(sent) if sent_start >= 0 else len(sent)

                            sent_chunk = {
                                "id": chunk_id,
                                "text": sent,
                                "parent_id": para_parent_id,
                                "level": "sentence",
                                "start_char": sent_start if sent_start >= 0 else 0,
                                "end_char": sent_end,
                                "token_count": count_tokens(sent, use_tiktoken=use_tiktoken, model=model),
                                "source_path": source_path,
                            }
                            chunks.append(sent_chunk)
                            chunk_id += 1

    elif 'paragraph' in levels:
        # Start with paragraphs if 'section' not in levels
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        for para in paragraphs:
            para_start = text.find(para)
            para_end = para_start + len(para) if para_start >= 0 else len(para)

            para_chunk = {
                "id": chunk_id,
                "text": para,
                "parent_id": None,
                "level": "paragraph",
                "start_char": para_start if para_start >= 0 else 0,
                "end_char": para_end,
                "token_count": count_tokens(para, use_tiktoken=use_tiktoken, model=model),
                "source_path": source_path,
            }
            chunks.append(para_chunk)
            para_parent_id = chunk_id
            chunk_id += 1

            if 'sentence' in levels:
                sentences = _split_into_sentences(para)

                for sent in sentences:
                    sent_start = text.find(sent)
                    sent_end = sent_start + len(sent) if sent_start >= 0 else len(sent)

                    sent_chunk = {
                        "id": chunk_id,
                        "text": sent,
                        "parent_id": para_parent_id,
                        "level": "sentence",
                        "start_char": sent_start if sent_start >= 0 else 0,
                        "end_char": sent_end,
                        "token_count": count_tokens(sent, use_tiktoken=use_tiktoken, model=model),
                        "source_path": source_path,
                    }
                    chunks.append(sent_chunk)
                    chunk_id += 1

    elif 'sentence' in levels:
        # Start with sentences if neither section nor paragraph in levels
        sentences = _split_into_sentences(text)

        for sent in sentences:
            sent_start = text.find(sent)
            sent_end = sent_start + len(sent) if sent_start >= 0 else len(sent)

            sent_chunk = {
                "id": chunk_id,
                "text": sent,
                "parent_id": None,
                "level": "sentence",
                "start_char": sent_start if sent_start >= 0 else 0,
                "end_char": sent_end,
                "token_count": count_tokens(sent, use_tiktoken=use_tiktoken, model=model),
                "source_path": source_path,
            }
            chunks.append(sent_chunk)
            chunk_id += 1

    # Fallback: if no chunks created, return entire text as one chunk
    if not chunks:
        chunks.append({
            "id": 0,
            "text": text,
            "parent_id": None,
            "level": "document",
            "start_char": 0,
            "end_char": len(text),
            "token_count": count_tokens(text, use_tiktoken=use_tiktoken, model=model),
            "source_path": source_path,
        })

    return chunks


def semantic_split(
    text: str,
    model: str = 'all-MiniLM-L6-v2',
    threshold: float = 0.7,
    use_tiktoken: bool = False,
    tiktoken_model: str = "gpt-3.5-turbo",
) -> List[Dict]:
    """Detect topic boundaries via semantic embeddings.

    Splits text at points where similarity with neighboring sentences drops
    below threshold (changepoint detection).

    Args:
        text: Text to chunk
        model: Sentence-transformers model name (default: 'all-MiniLM-L6-v2')
        threshold: Similarity threshold for splitting (0.0-1.0, default: 0.7)
        use_tiktoken: If True, use tiktoken for token counting
        tiktoken_model: Model name for tiktoken encoding

    Returns:
        List of chunk dictionaries with 'id', 'text', and 'token_count' keys
    """
    if not EMBEDDINGS_AVAILABLE:
        raise ImportError(
            "sentence-transformers is required for semantic-embedding strategy. "
            "Install with: pip install rag-chunk[embeddings]"
        )

    # Split into sentences
    sentences = _split_into_sentences(text)

    if len(sentences) <= 1:
        # Not enough sentences to split
        return [{
            "id": 0,
            "text": text,
            "token_count": count_tokens(text, use_tiktoken=use_tiktoken, model=tiktoken_model),
        }]

    # Load model and compute embeddings
    embedder = SentenceTransformer(model)
    embeddings = embedder.encode(sentences)

    # Compute cosine similarities between consecutive sentences
    similarities = []
    for i in range(len(embeddings) - 1):
        # Cosine similarity
        sim = np.dot(embeddings[i], embeddings[i + 1]) / (
            np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1])
        )
        similarities.append(sim)

    # Find split points where similarity drops below threshold
    split_indices = [0]  # Always start at beginning
    for i, sim in enumerate(similarities):
        if sim < threshold:
            split_indices.append(i + 1)
    split_indices.append(len(sentences))  # Always end at the end

    # Create chunks from split points
    chunks = []
    for i in range(len(split_indices) - 1):
        start_idx = split_indices[i]
        end_idx = split_indices[i + 1]
        chunk_sentences = sentences[start_idx:end_idx]
        chunk_text = ' '.join(chunk_sentences)

        chunks.append({
            "id": i,
            "text": chunk_text,
            "token_count": count_tokens(
                chunk_text,
                use_tiktoken=use_tiktoken,
                model=tiktoken_model
            ),
        })

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
    "hierarchical": (
        lambda text, chunk_size=0, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo", **kwargs:
            hierarchical_chunk(
                text,
                levels=kwargs.get('levels', ['section', 'paragraph']),
                use_tiktoken=use_tiktoken,
                model=model,
                source_path=kwargs.get('source_path', ''),
            )
    ),
    "semantic-embedding": (
        lambda text, chunk_size=0, overlap=0, use_tiktoken=False, model="gpt-3.5-turbo", **kwargs:
            semantic_split(
                text,
                model=kwargs.get('semantic_model', 'all-MiniLM-L6-v2'),
                threshold=kwargs.get('threshold', 0.7),
                use_tiktoken=use_tiktoken,
                tiktoken_model=model,
            )
    ),
}
