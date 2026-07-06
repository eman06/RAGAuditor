import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.claim_decontextualization import (
    build_decontextualization_prompt,
    decontextualize_claim,
    decontextualize_example,
)


def test_prompt_contains_required_context():
    prompt = build_decontextualization_prompt("What does the policy offer?", "The policy offers health insurance.", "It offers health insurance.")
    assert "Question:" in prompt
    assert "Answer sentence:" in prompt
    assert "Claim:" in prompt


def test_decontextualize_claim_uses_llm_when_available():
    rewritten = decontextualize_claim(
        "It expanded into Germany.",
        "What did the company do?",
        "The company expanded into Germany.",
        llm_client=lambda prompt: "The company expanded into Germany.",
    )
    assert rewritten == "The company expanded into Germany."


def test_decontextualize_example_adds_decontextualized_text():
    example = {
        "question": "What did the company do?",
        "claims": [{"text": "It expanded into Germany.", "source_sentence": "The company expanded into Germany."}],
    }
    rewritten = decontextualize_example(example, llm_client=lambda prompt: "The company expanded into Germany.")
    assert rewritten["claims"][0]["decontextualized_text"] == "The company expanded into Germany."
