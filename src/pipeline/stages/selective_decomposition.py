from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence


COMPLEX_MARKERS = [
    " and ",
    " but ",
    " while ",
    " although ",
    " because ",
    " therefore ",
    " as a result ",
    " higher than ",
    " lower than ",
    " more than ",
    " less than ",
    " compared to ",
    ",",
]


def is_complex(sentence: str) -> bool:
    """Heuristically mark a sentence as complex if it contains multiple signals."""
    text = sentence.lower().strip()
    if not text:
        return False

    signal_count = 0
    for marker in COMPLEX_MARKERS:
        if marker in text:
            signal_count += 1

    if re.search(r"\b\d+\b", text):
        signal_count += 1

    if re.search(r"\b(?:and|or|but|while|although|because|therefore|however)\b", text):
        signal_count += 1

    return signal_count >= 2


def split_claims(sentence: str) -> List[str]:
    """Backward-compatible fallback splitter for simple rule-based decomposition."""
    return split_claims_with_router(sentence, llm_client=None)


def split_claims_with_router(
    sentence: str,
    llm_client: Optional[Callable[[str], Sequence[str]]] = None,
) -> List[str]:
    """Route simple sentences directly and ask an LLM only for complex ones."""
    clean = sentence.strip()
    if not clean:
        return []

    if not is_complex(clean):
        return [clean]

    if llm_client is not None:
        try:
            claims = list(llm_client(clean))
            if claims:
                return [claim.strip() for claim in claims if claim and claim.strip()]
        except Exception:
            pass

    parts = re.split(r"\s+(and|but|while|although|because|however|therefore)\s+", clean, flags=re.IGNORECASE)
    claims = []
    current = []
    for part in parts:
        if part.lower() in {"and", "but", "while", "although", "because", "however", "therefore"}:
            if current:
                claims.append(" ".join(current).strip())
                current = []
            continue
        current.append(part)

    if current:
        claims.append(" ".join(current).strip())

    claims = [c for c in claims if c]
    return claims or [clean]


def decompose_example(example: Dict[str, Any]) -> Dict[str, Any]:
    """Create claim-level output from segmented sentence data."""
    example = dict(example)
    sentences = example.get("sentences", [])
    claims = []
    for sentence in sentences:
        decomposed = split_claims(sentence)
        for claim in decomposed:
            claims.append({
                "text": claim,
                "source_sentence": sentence,
                "complexity": "COMPLEX" if is_complex(sentence) else "SIMPLE",
            })
    example["claims"] = claims
    return example


def decompose_examples(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Decompose all examples."""
    return [decompose_example(example) for example in examples]


def process_stage3(input_path: str | Path, output_path: str | Path) -> List[Dict[str, Any]]:
    """Load segmented examples, decompose them into claims, and save the results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    decomposed_examples = decompose_examples(examples)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(decomposed_examples, handle, indent=2)

    return decomposed_examples
