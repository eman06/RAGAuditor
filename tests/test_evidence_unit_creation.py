import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.evidence_unit_creation import create_evidence_units


def test_create_evidence_units_returns_two_sentence_windows():
    contexts = [
        "Full-time employees are eligible for health insurance. Coverage begins after probation. Benefits include paid leave."
    ]
    units = create_evidence_units(contexts, window_size=2)
    assert len(units) == 3
    assert units[0]["span_id"] == "1_0"
    assert units[0]["text"] == "Full-time employees are eligible for health insurance. Coverage begins after probation."
    assert units[1]["text"] == "Coverage begins after probation. Benefits include paid leave."
