from __future__ import annotations

from typing import Any, Dict, List


def normalize_example(example: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a raw dataset example into the Stage 1 schema."""
    return {
        "id": example.get("id", ""),
        "question": example.get("query") or example.get("question", ""),
        "contexts": [example.get("context", "")] if example.get("context") else [],
        "answer": example.get("output") or example.get("answer", ""),
        "answer_label": example.get("hallucination_labels_processed") or example.get("answer_label", ""),
        "claim_annotations": [],
        "span_annotations": [],
    }


def normalize_examples(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize a list of raw examples."""
    return [normalize_example(example) for example in examples]
