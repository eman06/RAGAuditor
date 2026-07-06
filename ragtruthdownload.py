from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

try:
    from datasets import load_dataset
except ImportError:  # pragma: no cover - handled at runtime
    load_dataset = None

from src.pipeline.stages.data_loading import normalize_examples


def download_and_normalize(output_path: str | Path | None = None) -> List[dict[str, Any]]:
    """Download RAGTruth examples and normalize them into the Stage 1 schema."""
    if load_dataset is None:
        raise ImportError("The 'datasets' package is required to download RAGTruth data.")

    dataset = load_dataset("wandb/RAGTruth-processed", split="train")
    raw_examples = [dict(item) for item in dataset]
    normalized_examples = normalize_examples(raw_examples)

    destination = Path(output_path or "data/processed/ragtruth_normalized.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(normalized_examples, handle, indent=2)

    print(f"Total rows loaded: {len(dataset)}")
    print(f"Normalized rows saved to: {destination}")
    return normalized_examples


if __name__ == "__main__":
    download_and_normalize()
