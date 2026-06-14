"""
Pure-Python TF-IDF and cosine similarity helpers.

This module replaces the scikit-learn dependency used by Step 3 so the
project installs cleanly on Windows without a C/C++ build toolchain.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List


TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "in", "is", "it", "of", "on", "or", "that",
    "the", "to", "was", "were", "with", "within", "may", "this",
    "which", "while", "into", "than", "then", "their", "there", "been",
    "being", "can", "could", "should", "would", "will", "not", "no",
}


def tokenize(text: str) -> List[str]:
    tokens = TOKEN_PATTERN.findall(text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def _normalize(vector: Dict[str, float]) -> Dict[str, float]:
    norm = math.sqrt(sum(value * value for value in vector.values()))
    if norm == 0:
        return {}
    return {term: value / norm for term, value in vector.items()}


def _tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    if not tokens:
        return {}

    counts = Counter(tokens)
    total = len(tokens)
    vector: Dict[str, float] = {}
    for term, count in counts.items():
        if term not in idf:
            continue
        tf = count / total
        vector[term] = tf * idf[term]
    return _normalize(vector)


@dataclass(frozen=True)
class TfidfModel:
    idf: Dict[str, float]
    doc_vectors: List[Dict[str, float]]


def fit_tfidf(documents: Iterable[str]) -> TfidfModel:
    tokenized_docs = [tokenize(document) for document in documents]
    doc_freq: Counter[str] = Counter()

    for tokens in tokenized_docs:
        doc_freq.update(set(tokens))

    total_docs = len(tokenized_docs)
    idf = {
        term: math.log((1 + total_docs) / (1 + freq)) + 1.0
        for term, freq in doc_freq.items()
    }
    doc_vectors = [_tfidf_vector(tokens, idf) for tokens in tokenized_docs]
    return TfidfModel(idf=idf, doc_vectors=doc_vectors)


def transform(text: str, model: TfidfModel) -> Dict[str, float]:
    return _tfidf_vector(tokenize(text), model.idf)


def cosine_similarity(query_vector: Dict[str, float], doc_vectors: List[Dict[str, float]]) -> List[float]:
    if not query_vector:
        return [0.0 for _ in doc_vectors]

    scores: List[float] = []
    for doc_vector in doc_vectors:
        score = 0.0
        smaller, larger = (query_vector, doc_vector)
        if len(doc_vector) < len(query_vector):
            smaller, larger = doc_vector, query_vector

        for term, value in smaller.items():
            score += value * larger.get(term, 0.0)
        scores.append(score)

    return scores
