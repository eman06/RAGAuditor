from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def split_into_sentences(text: str) -> List[str]:
    """Split a text into sentences using a simple regex-based tokenizer."""
    if not text:
        return []
    import re

    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def create_evidence_units(contexts: List[str], window_size: int = 2) -> List[Dict[str, Any]]:
    """Create sliding-window evidence units from context chunks."""
    units: List[Dict[str, Any]] = []
    for chunk_idx, chunk in enumerate(contexts, start=1):
        sentences = split_into_sentences(chunk)
        if not sentences:
            continue

        for start in range(0, len(sentences)):
            end = start + window_size
            window = sentences[start:end]
            if not window:
                continue
            units.append(
                {
                    "chunk_id": chunk_idx,
                    "span_id": f"{chunk_idx}_{start}",
                    "text": " ".join(window),
                }
            )
    return units


def build_evidence_units(example: Dict[str, Any], window_size: int = 2) -> Dict[str, Any]:
    """Add evidence units to an example."""
    example = dict(example)
    contexts = example.get("contexts", [])
    example["evidence_units"] = create_evidence_units(contexts, window_size=window_size)
    return example


def build_evidence_units_for_examples(examples: List[Dict[str, Any]], window_size: int = 2) -> List[Dict[str, Any]]:
    """Apply evidence unit creation to a list of examples."""
    return [build_evidence_units(example, window_size=window_size) for example in examples]


def process_stage5(input_path: str | Path, output_path: str | Path, window_size: int = 2) -> List[Dict[str, Any]]:
    """Load examples, create evidence units, and save the results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    processed_examples = build_evidence_units_for_examples(examples, window_size=window_size)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(processed_examples, handle, indent=2)

    return processed_examples
