"""Scoring and retrieval utilities."""

import json
import math
from typing import Dict, List, Tuple


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


def retrieve_top_k(chunks: List[Dict], query: str, k: int) -> List[Dict]:
    """Return top k chunks by similarity."""
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


def evaluate_strategy(
    chunks: List[Dict], questions: List[Dict], top_k: int
) -> Tuple[float, List[Dict]]:
    """Return average recall and per-question details."""
    per = []
    recalls = []
    for q in questions:
        question = q.get("question", "")
        relevant = q.get("relevant", [])
        retrieved = retrieve_top_k(chunks, question, top_k)
        recall = compute_recall(retrieved, relevant)
        recalls.append(recall)
        per.append({"question": question, "recall": recall})
    avg = sum(recalls) / len(recalls) if recalls else 0.0
    return avg, per
