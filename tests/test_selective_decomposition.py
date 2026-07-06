import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.stages.selective_decomposition import (
    decompose_example,
    is_complex,
    split_claims,
    split_claims_with_router,
)


def test_simple_sentence_stays_single_claim():
    sentence = "The company was founded in 2015."
    assert split_claims(sentence) == [sentence]
    assert not is_complex(sentence)


def test_complex_sentence_is_split_into_multiple_claims():
    sentence = "The company was founded in 2015 and raised $20 million in 2021."
    claims = split_claims(sentence)
    assert claims == ["The company was founded in 2015", "raised $20 million in 2021."]


def test_decompose_example_adds_claims_field():
    example = {"id": "ex-1", "sentences": ["The policy covers health insurance and paid leave."]}
    decomposed = decompose_example(example)
    assert "claims" in decomposed
    assert len(decomposed["claims"]) >= 1


def test_router_bypasses_llm_for_simple_sentence():
    sentence = "The company was founded in 2015."
    result = split_claims_with_router(sentence, llm_client=lambda _: ["should not be used"])
    assert result == [sentence]
