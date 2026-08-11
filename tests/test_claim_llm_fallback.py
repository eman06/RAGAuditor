import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.claim_llm_fallback import (
    build_llm_judge_prompt,
    should_use_llm_judge,
    attach_llm_fallback,
)


def test_should_use_llm_judge_for_uncertain_confidence():
    assert should_use_llm_judge(0.5) is True
    assert should_use_llm_judge(0.4) is True
    assert should_use_llm_judge(0.7) is True


def test_should_not_use_llm_judge_for_certain_confidence():
    assert should_use_llm_judge(0.2) is False
    assert should_use_llm_judge(0.9) is False


def test_build_llm_judge_prompt_contains_required_fields():
    prompt = build_llm_judge_prompt(
        "What did the company do?",
        "The company raised $20 million.",
        "The company closed a Series A round."
    )
    assert "Question:" in prompt
    assert "Claim:" in prompt
    assert "Evidence:" in prompt
    assert "SUPPORTED" in prompt
    assert "PARTIALLY_SUPPORTED" in prompt


def test_attach_llm_fallback_adds_field_when_uncertain():
    example = {
        "question": "What did the company do?",
        "claims": [
            {
                "text": "The company raised money.",
                "decontextualized_text": "The company raised money.",
                "verification": {"label": "SUPPORTED", "confidence": 0.5},
                "top_evidence": [{"span": "The company raised $20 million."}]
            }
        ]
    }
    # Mock LLM judge that returns a fixed result
    class MockLLMJudge:
        def judge(self, q, c, e):
            return {"label": "SUPPORTED", "reason": "test"}
    
    enriched = attach_llm_fallback(example, llm_judge=MockLLMJudge())
    assert "llm_fallback" in enriched["claims"][0]
