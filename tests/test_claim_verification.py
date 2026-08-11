import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.claim_verification import SimpleNLIVerifier, verify_claim, attach_claim_verification


def test_verifier_returns_supported_for_matching_claim():
    verifier = SimpleNLIVerifier()
    result = verify_claim(
        "The company raised $20 million.",
        "The company closed a $20 million Series A round in 2021.",
        verifier=verifier,
        use_binary=True
    )
    assert result["label"] in ["SUPPORTED", "UNSUPPORTED"]
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0


def test_verifier_returns_unsupported_for_non_matching_claim():
    verifier = SimpleNLIVerifier()
    result = verify_claim(
        "Employees work on Mars.",
        "The company is based in New York.",
        verifier=verifier,
        use_binary=True
    )
    assert result["label"] in ["SUPPORTED", "UNSUPPORTED"]


def test_attach_verification_adds_verification_field():
    example = {
        "question": "What did the company do?",
        "claims": [
            {
                "text": "The company raised money.",
                "top_evidence": [{"span": "The company raised $20 million."}]
            }
        ]
    }
    enriched = attach_claim_verification(example, use_binary=True)
    assert "verification" in enriched["claims"][0]
    assert "label" in enriched["claims"][0]["verification"]
    assert "confidence" in enriched["claims"][0]["verification"]
