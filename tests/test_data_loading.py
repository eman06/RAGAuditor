import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.data_loading import normalize_example


def test_normalize_example_creates_required_schema():
    raw_example = {
        "id": "ex-1",
        "question": "What is the policy?",
        "contexts": ["Chunk A", "Chunk B"],
        "answer": "The policy covers health insurance.",
        "answer_label": "faithful",
    }

    normalized = normalize_example(raw_example)

    assert normalized["id"] == "ex-1"
    assert normalized["question"] == "What is the policy?"
    assert normalized["contexts"] == ["Chunk A", "Chunk B"]
    assert normalized["answer"] == "The policy covers health insurance."
    assert normalized["answer_label"] == "faithful"
    assert normalized["claim_annotations"] == []
    assert normalized["span_annotations"] == []
