import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.answer_risk_aggregation import (
    calculate_claim_ratios,
    calculate_risk_score,
    classify_risk_level,
    aggregate_answer_risk,
)


def test_calculate_claim_ratios():
    claims = [
        {"verification": {"label": "SUPPORTED", "confidence": 0.9}},
        {"verification": {"label": "UNSUPPORTED", "confidence": 0.3}},
        {"verification": {"label": "CONTRADICTED", "confidence": 0.2}},
    ]
    ratios = calculate_claim_ratios(claims)
    assert ratios["supported_ratio"] == 1/3
    assert ratios["unsupported_ratio"] == 1/3
    assert ratios["contradicted_ratio"] == 1/3


def test_calculate_risk_score():
    score = calculate_risk_score(
        unsupported_ratio=0.2,
        contradicted_ratio=0.1,
        partial_support_ratio=0.05,
        average_uncertainty=0.5
    )
    expected = 0.45 * 0.2 + 0.30 * 0.1 + 0.15 * 0.05 + 0.10 * 0.5
    assert score == round(expected, 3)


def test_classify_risk_level_low():
    assert classify_risk_level(0.1) == "LOW"
    assert classify_risk_level(0.25) == "LOW"


def test_classify_risk_level_medium():
    assert classify_risk_level(0.26) == "MEDIUM"
    assert classify_risk_level(0.5) == "MEDIUM"


def test_classify_risk_level_high():
    assert classify_risk_level(0.51) == "HIGH"
    assert classify_risk_level(0.75) == "HIGH"


def test_classify_risk_level_critical():
    assert classify_risk_level(0.76) == "CRITICAL"
    assert classify_risk_level(1.0) == "CRITICAL"


def test_aggregate_answer_risk_adds_risk_field():
    example = {
        "question": "What did the company do?",
        "answer": "The company expanded.",
        "claims": [
            {"verification": {"label": "SUPPORTED", "confidence": 0.8}},
            {"verification": {"label": "UNSUPPORTED", "confidence": 0.3}},
        ]
    }
    aggregated = aggregate_answer_risk(example)
    assert "answer_risk" in aggregated
    assert "risk_score" in aggregated["answer_risk"]
    assert "risk_level" in aggregated["answer_risk"]
    assert "total_claims" in aggregated["answer_risk"]
