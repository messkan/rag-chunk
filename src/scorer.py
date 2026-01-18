"""Scoring and retrieval utilities."""

import json
import math
from typing import Dict, List, Tuple, Optional

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None
    np = None

# Global embedding model cache
_embedding_model = None


def load_test_file(path: str) -> List[Dict]:
    """Load test file returning list of question dicts."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "questions" in data:
        data = data["questions"]
    return data


def chunk_similarity(chunk_text: str, query: str) -> float:
    """Simple lexical similarity based on overlapping unique words."""
    c_words = set(w.lower() for w in chunk_text.split())
    q_words = set(w.lower() for w in query.split())
    if not c_words or not q_words:
        return 0.0
    inter = len(c_words & q_words)
    denom = math.sqrt(len(c_words) * len(q_words))
    return inter / denom if denom else 0.0


def get_embedding_model():
    """Get or initialize the global embedding model."""
    global _embedding_model
    if _embedding_model is None:
        if not EMBEDDINGS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for semantic retrieval. "
                "Install with: pip install rag-chunk[semantic]"
            )
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def semantic_similarity(chunk_text: str, query: str) -> float:
    """Compute cosine similarity using sentence embeddings.

    Args:
        chunk_text: Text of the chunk
        query: Query text

    Returns:
        Cosine similarity score (0-1)
    """
    if not EMBEDDINGS_AVAILABLE:
        raise ImportError(
            "sentence-transformers is required for semantic similarity. "
            "Install with: pip install rag-chunk[semantic]"
        )

    model = get_embedding_model()
    embeddings = model.encode([chunk_text, query])
    chunk_emb = embeddings[0]
    query_emb = embeddings[1]

    # Cosine similarity
    similarity = np.dot(chunk_emb, query_emb) / (
        np.linalg.norm(chunk_emb) * np.linalg.norm(query_emb)
    )
    return float(similarity)


def retrieve_top_k(
    chunks: List[Dict], query: str, k: int, use_embeddings: bool = False
) -> List[Dict]:
    """Return top k chunks by similarity.

    Args:
        chunks: List of chunk dictionaries
        query: Query text
        k: Number of chunks to retrieve
        use_embeddings: If True, use semantic similarity; otherwise lexical

    Returns:
        Top k most similar chunks
    """
    if use_embeddings:
        scored = [(semantic_similarity(c["text"], query), c) for c in chunks]
    else:
        scored = [(chunk_similarity(c["text"], query), c) for c in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]


def compute_recall(retrieved: List[Dict], relevant_phrases: List[str]) -> float:
    """Recall of relevant phrases contained in retrieved chunks."""
    if not relevant_phrases:
        return 0.0
    found = 0
    lower_texts = [c["text"].lower() for c in retrieved]
    for phrase in relevant_phrases:
        lp = phrase.lower()
        if any(lp in t for t in lower_texts):
            found += 1
    return found / len(relevant_phrases)


def compute_precision_recall_f1(
    retrieved: List[Dict], relevant_phrases: List[str]
) -> Tuple[float, float, float]:
    """Compute precision, recall, and F1 score.

    Args:
        retrieved: List of retrieved chunk dictionaries
        relevant_phrases: List of phrases that should be found

    Returns:
        Tuple of (precision, recall, f1)
    """
    if not relevant_phrases:
        return 0.0, 0.0, 0.0

    lower_texts = [c["text"].lower() for c in retrieved]
    found_phrases = set()
    for phrase in relevant_phrases:
        lp = phrase.lower()
        if any(lp in t for t in lower_texts):
            found_phrases.add(phrase)

    tp = len(found_phrases)  # True positives
    fn = len(relevant_phrases) - tp  # False negatives
    # For precision: assume each relevant phrase found is a "correct" retrieval
    # FP = 0 in this simplified model (we only check relevant phrases)
    fp = 0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return precision, recall, f1


def evaluate_strategy(
    chunks: List[Dict], questions: List[Dict], top_k: int, use_embeddings: bool = False
) -> Tuple[Dict, List[Dict]]:
    """Return average metrics and per-question details.

    Args:
        chunks: List of chunk dictionaries
        questions: List of question dictionaries
        top_k: Number of chunks to retrieve per question
        use_embeddings: If True, use semantic similarity for retrieval

    Returns:
        Tuple of (metrics_dict, per_question_list)
        metrics_dict contains: avg_recall, avg_precision, avg_f1
    """
    per = []
    recalls = []
    precisions = []
    f1s = []
    for q in questions:
        question = q.get("question", "")
        relevant = q.get("relevant", [])
        retrieved = retrieve_top_k(chunks, question, top_k, use_embeddings)
        precision, recall, f1 = compute_precision_recall_f1(retrieved, relevant)
        recalls.append(recall)
        precisions.append(precision)
        f1s.append(f1)
        per.append(
            {"question": question, "recall": recall, "precision": precision, "f1": f1}
        )

    metrics = {
        "avg_recall": sum(recalls) / len(recalls) if recalls else 0.0,
        "avg_precision": sum(precisions) / len(precisions) if precisions else 0.0,
        "avg_f1": sum(f1s) / len(f1s) if f1s else 0.0,
    }
    return metrics, per
