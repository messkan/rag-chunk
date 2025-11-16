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
    avg, _ = scorer.evaluate_strategy(chunks, questions, top_k=1)
    assert 0.0 <= avg <= 1.0
