"""Basic tests for rag-chunk pipeline."""

from src import chunker, parser, scorer


def test_parser_clean():
    """Ensure markdown cleaning collapses excessive blank lines."""
    docs = [("a.md", "Hello\n\nWorld\n\n\nAgain")]
    text = parser.clean_markdown_text(docs)
    assert "Again" in text
    assert "\n\n\n" not in text


def test_fixed_size_chunking():
    """Fixed-size chunking splits text into expected number of chunks."""
    text = "one two three four five six seven eight nine ten"
    chunks = chunker.fixed_size_chunks(text, 3)
    assert len(chunks) == 4
    assert chunks[0]["text"].startswith("one")


def test_sliding_window_chunking():
    """Sliding-window produces overlapping chunks as expected."""
    text = " ".join(str(i) for i in range(1, 21))
    chunks = chunker.sliding_window_chunks(text, 5, 2)
    assert chunks[1]["id"] == 1
    assert len(chunks) > 0


def test_paragraph_chunking():
    """Paragraph chunking splits text by blank lines."""
    text = "Para one\n\nPara two\n\nPara three"
    chunks = chunker.paragraph_chunks(text)
    assert len(chunks) == 3


def test_recall():
    """Evaluate recall computation returns a value within expected range."""
    chunks = [
        {"id": 0, "text": "retrieval augmented generation"},
        {"id": 1, "text": "other text"},
    ]
    questions = [
        {"question": "What about generation?", "relevant": ["generation", "retrieval"]}
    ]
    metrics, _ = scorer.evaluate_strategy(chunks, questions, top_k=1)
    assert 0.0 <= metrics["avg_recall"] <= 1.0


def test_token_counting_without_tiktoken():
    """Test word-based token counting (default behavior)."""
    text = "Hello world this is a test"
    count = chunker.count_tokens(text, use_tiktoken=False)
    assert count == 6


def test_tiktoken_chunking_availability():
    """Test that tiktoken functions handle import gracefully."""
    text = "Sample text for testing"
    try:
        # This will work if tiktoken is installed
        count = chunker.count_tokens(text, use_tiktoken=True)
        assert count > 0
        # Test chunking with tiktoken
        chunks = chunker.fixed_size_chunks(text, chunk_size=5, use_tiktoken=True)
        assert len(chunks) > 0
    except ImportError as e:
        # Expected if tiktoken is not installed
        assert "tiktoken" in str(e).lower()


def test_fixed_size_chunks_with_tiktoken_flag():
    """Test that use_tiktoken parameter is accepted by chunking functions."""
    text = "one two three four five six"
    # Should work with use_tiktoken=False (default behavior)
    chunks = chunker.fixed_size_chunks(text, chunk_size=3, use_tiktoken=False)
    assert len(chunks) == 2
    assert "one" in chunks[0]["text"]


def test_sliding_window_with_tiktoken_flag():
    """Test sliding window accepts tiktoken flag."""
    text = " ".join(str(i) for i in range(1, 11))
    chunks = chunker.sliding_window_chunks(
        text, chunk_size=4, overlap=1, use_tiktoken=False
    )
    assert len(chunks) > 0


def test_hierarchical_chunking_sections():
    """Test hierarchical chunking with sections."""
    text = """# Introduction
This is the introduction paragraph.

## Section 1
First section content.

## Section 2
Second section content."""
    
    chunks = chunker.hierarchical_chunk(text, levels=['section'])
    assert len(chunks) > 0
    # Check that chunks have expected metadata
    assert all('level' in chunk for chunk in chunks)
    assert all('parent_id' in chunk for chunk in chunks)
    assert all('token_count' in chunk for chunk in chunks)


def test_hierarchical_chunking_paragraphs():
    """Test hierarchical chunking with paragraphs."""
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    
    chunks = chunker.hierarchical_chunk(text, levels=['paragraph'])
    assert len(chunks) >= 3
    # Check paragraph level chunks exist
    para_chunks = [c for c in chunks if c['level'] == 'paragraph']
    assert len(para_chunks) >= 3


def test_hierarchical_chunking_sentences():
    """Test hierarchical chunking with sentences."""
    text = "First sentence. Second sentence. Third sentence."
    
    chunks = chunker.hierarchical_chunk(text, levels=['sentence'])
    assert len(chunks) >= 3
    # Check sentence level chunks exist
    sent_chunks = [c for c in chunks if c['level'] == 'sentence']
    assert len(sent_chunks) >= 3


def test_hierarchical_chunking_multi_level():
    """Test hierarchical chunking with multiple levels."""
    text = """# Header
Paragraph one. Sentence two.

Paragraph two. Sentence two."""
    
    chunks = chunker.hierarchical_chunk(text, levels=['section', 'paragraph', 'sentence'])
    assert len(chunks) > 0
    # Check multiple levels exist
    levels = set(c['level'] for c in chunks)
    assert 'section' in levels or 'paragraph' in levels or 'sentence' in levels


def test_semantic_split_availability():
    """Test that semantic split handles import gracefully."""
    text = "First topic here. More on first topic. Now second topic begins. More on second."
    
    try:
        chunks = chunker.semantic_split(text, threshold=0.5)
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)
    except ImportError as e:
        # Expected if sentence-transformers is not installed
        assert "sentence-transformers" in str(e).lower()


def test_semantic_split_single_sentence():
    """Test semantic split with single sentence fallback."""
    text = "Only one sentence here."
    
    try:
        chunks = chunker.semantic_split(text)
        assert len(chunks) == 1
        assert chunks[0]['text'] == text
    except ImportError:
        # Expected if sentence-transformers is not installed
        pass
