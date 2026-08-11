from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def calculate_claim_ratios(claims: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate the ratios of different claim label types."""
    if not claims:
        return {
            "supported_ratio": 0.0,
            "unsupported_ratio": 0.0,
            "contradicted_ratio": 0.0,
            "partial_support_ratio": 0.0,
            "average_confidence": 0.0,
        }

    total = len(claims)
    supported_count = 0
    unsupported_count = 0
    contradicted_count = 0
    partial_support_count = 0
    confidence_sum = 0.0

    for claim in claims:
        if not isinstance(claim, dict):
            continue

        verification = claim.get("verification", {})
        label = verification.get("label", "UNSUPPORTED")
        confidence = verification.get("confidence", 0.0)

        confidence_sum += confidence

        if label == "SUPPORTED":
            supported_count += 1
        elif label == "UNSUPPORTED":
            unsupported_count += 1
        elif label == "CONTRADICTED":
            contradicted_count += 1
        elif label == "PARTIALLY_SUPPORTED":
            partial_support_count += 1

    average_confidence = confidence_sum / total if total > 0 else 0.0
    average_uncertainty = 1.0 - average_confidence

    return {
        "supported_ratio": supported_count / total,
        "unsupported_ratio": unsupported_count / total,
        "contradicted_ratio": contradicted_count / total,
        "partial_support_ratio": partial_support_count / total,
        "average_confidence": average_confidence,
        "average_uncertainty": average_uncertainty,
    }


def calculate_risk_score(
    unsupported_ratio: float,
    contradicted_ratio: float,
    partial_support_ratio: float,
    average_uncertainty: float,
) -> float:
    """Calculate the answer-level hallucination risk score."""
    score = (
        0.45 * unsupported_ratio +
        0.30 * contradicted_ratio +
        0.15 * partial_support_ratio +
        0.10 * average_uncertainty
    )
    return round(min(1.0, max(0.0, score)), 3)


def classify_risk_level(risk_score: float) -> str:
    """Classify risk score into a risk level."""
    if risk_score <= 0.25:
        return "LOW"
    elif risk_score <= 0.50:
        return "MEDIUM"
    elif risk_score <= 0.75:
        return "HIGH"
    else:
        return "CRITICAL"


def aggregate_answer_risk(example: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate answer-level risk metrics for an example."""
    example = dict(example)
    claims = example.get("claims", [])
    answer = example.get("answer", "")

    ratios = calculate_claim_ratios(claims)
    risk_score = calculate_risk_score(
        ratios["unsupported_ratio"],
        ratios["contradicted_ratio"],
        ratios["partial_support_ratio"],
        ratios["average_uncertainty"],
    )
    risk_level = classify_risk_level(risk_score)

    example["answer_risk"] = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "total_claims": len(claims),
        "supported_count": round(ratios["supported_ratio"] * len(claims)),
        "unsupported_count": round(ratios["unsupported_ratio"] * len(claims)),
        "contradicted_count": round(ratios["contradicted_ratio"] * len(claims)),
        "partial_support_count": round(ratios["partial_support_ratio"] * len(claims)),
        "average_confidence": round(ratios["average_confidence"], 3),
        "metrics": ratios,
    }

    return example


def aggregate_examples(examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply answer-level risk aggregation to all examples."""
    return [aggregate_answer_risk(example) for example in examples]


def process_stage9(
    input_path: str | Path,
    output_path: str | Path,
) -> List[Dict[str, Any]]:
    """Load claim verification results, aggregate to answer level, and save results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    aggregated_examples = aggregate_examples(examples)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(aggregated_examples, handle, indent=2)

    return aggregated_examples
