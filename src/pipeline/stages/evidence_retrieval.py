from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    from rank_bm25 import BM25Okapi
except ImportError:  # pragma: no cover
    BM25Okapi = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover
    SentenceTransformer = None


class SimpleHybridRetriever:
    """A lightweight hybrid retriever using BM25 and dense cosine similarity."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None
        if SentenceTransformer is not None:
            try:
                self._model = SentenceTransformer(model_name)
            except Exception:
                self._model = None

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def _build_bm25(self, corpus: List[str]):
        if BM25Okapi is None:
            return None
        tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        return BM25Okapi(tokenized_corpus)

    def _dense_embeddings(self, texts: List[str]) -> List[List[float]]:
        if self._model is None:
            return []
        return self._model.encode(texts, convert_to_numpy=False).tolist()

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def _token_overlap_score(self, claim: str, text: str) -> float:
        claim_tokens = set(self._tokenize(claim))
        text_tokens = set(self._tokenize(text))
        if not claim_tokens or not text_tokens:
            return 0.0
        overlap = claim_tokens & text_tokens
        return len(overlap) / max(1, len(claim_tokens | text_tokens))

    def retrieve(self, claim: str, evidence_units: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        if not evidence_units:
            return []

        corpus = [unit.get("text", "") for unit in evidence_units]
        bm25 = self._build_bm25(corpus)
        dense_embeddings = self._dense_embeddings([claim] + corpus) if self._model is not None else []
        claim_embedding = dense_embeddings[0] if dense_embeddings else None
        unit_embeddings = dense_embeddings[1:] if dense_embeddings else []

        scored: List[Tuple[float, Dict[str, Any]]] = []
        for idx, unit in enumerate(evidence_units):
            text = unit.get("text", "")
            bm25_score = self._token_overlap_score(claim, text)
            dense_score = self._token_overlap_score(claim, text)
            if bm25 is not None:
                bm25_score = float(bm25.get_scores(self._tokenize(claim))[idx])
            if claim_embedding is not None and idx < len(unit_embeddings):
                dense_score = self._cosine_similarity(claim_embedding, unit_embeddings[idx])
            hybrid_score = 0.5 * bm25_score + 0.5 * dense_score
            scored.append((hybrid_score, unit))

        scored.sort(key=lambda item: item[0], reverse=True)
        top_results = []
        for score, unit in scored[:top_k]:
            top_results.append(
                {
                    "span": unit.get("text", ""),
                    "score": round(score, 3),
                }
            )
        return top_results


def retrieve_claim_evidence(example: Dict[str, Any], retriever: SimpleHybridRetriever | None = None, top_k: int = 3) -> Dict[str, Any]:
    """Attach top evidence spans to each claim in an example."""
    example = dict(example)
    claims = example.get("claims", [])
    evidence_units = example.get("evidence_units", [])
    if retriever is None:
        retriever = SimpleHybridRetriever()

    enriched_claims = []
    for claim in claims:
        if isinstance(claim, dict):
            claim_text = claim.get("decontextualized_text") or claim.get("text", "")
            top_evidence = retriever.retrieve(claim_text, evidence_units, top_k=top_k)
            updated_claim = dict(claim)
            updated_claim["top_evidence"] = top_evidence
            enriched_claims.append(updated_claim)
        else:
            enriched_claims.append(claim)

    example["claims"] = enriched_claims
    return example


def retrieve_evidence_for_examples(examples: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """Apply claim-level evidence retrieval to a list of examples."""
    retriever = SimpleHybridRetriever()
    return [retrieve_claim_evidence(example, retriever=retriever, top_k=top_k) for example in examples]


def process_stage6(input_path: str | Path, output_path: str | Path, top_k: int = 3) -> List[Dict[str, Any]]:
    """Load evidence-unit examples, retrieve top evidence spans for each claim, and save the results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    processed_examples = retrieve_evidence_for_examples(examples, top_k=top_k)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(processed_examples, handle, indent=2)

    return processed_examples
