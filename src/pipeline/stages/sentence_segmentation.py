from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    import spacy
except ImportError:  # pragma: no cover
    spacy = None


def split_sentences(text: str, model: str = "en_core_web_sm") -> List[str]:
    """Split a text into sentences using spaCy if available, otherwise fallback to a simple regex."""
    if not text or not text.strip():
        return []

    if spacy is not None:
        try:
            nlp = spacy.load(model)
        except OSError:
            nlp = spacy.blank("en")
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    import re

    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p]


def segment_answer(example: Dict[str, Any]) -> Dict[str, Any]:
    """Add sentence segmentation output to an example dictionary."""
    sentences = split_sentences(example.get("answer", ""))
    example = dict(example)
    example["sentences"] = sentences
    return example


def segment_examples(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Segment all examples in a dataset."""
    return [segment_answer(example) for example in examples]


def process_stage2(input_path: str | Path, output_path: str | Path) -> List[Dict[str, Any]]:
    """Load normalized examples, segment their answers, and save the results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    segmented_examples = segment_examples(examples)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(segmented_examples, handle, indent=2)

    return segmented_examples
