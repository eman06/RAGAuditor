import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.evidence_retrieval import SimpleHybridRetriever


def test_retriever_returns_top_evidence():
    retriever = SimpleHybridRetriever(model_name="all-MiniLM-L6-v2")
    evidence_units = [
        {"text": "The company closed a $20 million Series A round in 2021."},
        {"text": "The company expanded into Germany in 2022."},
    ]
    result = retriever.retrieve("The company raised $20 million in 2021.", evidence_units, top_k=1)
    assert len(result) == 1
    assert result[0]["span"] == "The company closed a $20 million Series A round in 2021."
