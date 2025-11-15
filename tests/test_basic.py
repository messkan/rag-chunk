"""Basic tests for rag-chunk pipeline."""
from src import parser, chunker, scorer

def test_parser_clean():
    docs = [("a.md", "Hello\n\nWorld\n\n\nAgain")] 
    text = parser.clean_markdown_text(docs)
    assert "Again" in text
    assert "\n\n\n" not in text

def test_fixed_size_chunking():
    text = "one two three four five six seven eight nine ten"
    chunks = chunker.fixed_size_chunks(text, 3)
    assert len(chunks) == 4
    assert chunks[0]["text"].startswith("one")

def test_sliding_window_chunking():
    text = " ".join(str(i) for i in range(1, 21))
    chunks = chunker.sliding_window_chunks(text, 5, 2)
    assert chunks[1]["id"] == 1
    assert len(chunks) > 0

def test_paragraph_chunking():
    text = "Para one\n\nPara two\n\nPara three"
    chunks = chunker.paragraph_chunks(text)
    assert len(chunks) == 3

def test_recall():
    chunks = [{"id":0,"text":"retrieval augmented generation"},{"id":1,"text":"other text"}]
    questions = [{"question":"What about generation?","relevant":["generation","retrieval"]}]
    avg, per = scorer.evaluate_strategy(chunks, questions, top_k=1)
    assert avg <= 1.0
