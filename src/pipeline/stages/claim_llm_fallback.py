from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

try:
    import ollama
except ImportError:  # pragma: no cover
    ollama = None


def build_llm_judge_prompt(question: str, claim: str, evidence: str) -> str:
    """Build the LLM judge prompt for extended label classification."""
    return (
        "You are checking whether a RAG answer claim is supported by the retrieved evidence.\n\n"
        f"Question:\n{question}\n\n"
        f"Claim:\n{claim}\n\n"
        f"Evidence:\n{evidence}\n\n"
        "Choose one label:\n"
        "SUPPORTED - the evidence fully supports the claim.\n"
        "PARTIALLY_SUPPORTED - the evidence supports part of the claim but not all of it.\n"
        "UNSUPPORTED - the evidence does not support the claim.\n"
        "CONTRADICTED - the evidence contradicts the claim.\n\n"
        'Return JSON only:\n'
        '{"label": "...", "reason": "short reason"}'
    )


class LLMJudge:
    """An LLM-based judge for uncertain verification results."""

    def __init__(
        self,
        provider: str = "ollama",
        model: str = "llama2",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self._client = None

        if provider == "openai" and OpenAI is not None:
            try:
                self._client = OpenAI(api_key=api_key or "")
            except Exception:
                pass
        elif provider == "ollama" and ollama is not None:
            self._client = ollama

    def judge(self, question: str, claim: str, evidence: str) -> Dict[str, Any]:
        """Get an LLM judgment on claim verification."""
        prompt = build_llm_judge_prompt(question, claim, evidence)

        if self.provider == "openai" and self._client is not None:
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=200,
                )
                content = response.choices[0].message.content
                result = json.loads(content)
                return result
            except Exception:
                pass

        elif self.provider == "ollama" and self._client is not None:
            try:
                response = self._client.generate(model=self.model, prompt=prompt, stream=False)
                content = response.get("response", "")
                result = json.loads(content)
                return result
            except Exception:
                pass

        return {"label": "UNSUPPORTED", "reason": "LLM judge unavailable; falling back to verifier result."}


def should_use_llm_judge(confidence: float, threshold_min: float = 0.40, threshold_max: float = 0.70) -> bool:
    """Determine if LLM judge should be used based on confidence thresholds."""
    return threshold_min <= confidence <= threshold_max


def attach_llm_fallback(
    example: Dict[str, Any],
    llm_judge: Optional[LLMJudge] = None,
    confidence_min: float = 0.40,
    confidence_max: float = 0.70,
) -> Dict[str, Any]:
    """Attach LLM fallback results to claims with uncertain verification scores."""
    example = dict(example)
    claims = example.get("claims", [])
    question = example.get("question", "")
    
    if llm_judge is None:
        llm_judge = LLMJudge(provider="ollama", model="llama2")

    enriched_claims = []
    for claim in claims:
        if isinstance(claim, dict):
            verification = claim.get("verification", {})
            confidence = verification.get("confidence", 0.0)

            if should_use_llm_judge(confidence, threshold_min=confidence_min, threshold_max=confidence_max):
                top_evidence = claim.get("top_evidence", [])
                if top_evidence:
                    evidence_text = top_evidence[0].get("span", "")
                    claim_text = claim.get("decontextualized_text") or claim.get("text", "")
                    llm_result = llm_judge.judge(question, claim_text, evidence_text)
                    updated_claim = dict(claim)
                    updated_claim["llm_fallback"] = llm_result
                    enriched_claims.append(updated_claim)
                else:
                    enriched_claims.append(claim)
            else:
                enriched_claims.append(claim)
        else:
            enriched_claims.append(claim)

    example["claims"] = enriched_claims
    return example


def apply_llm_fallback_to_examples(
    examples: List[Dict[str, Any]],
    llm_judge: Optional[LLMJudge] = None,
    confidence_min: float = 0.40,
    confidence_max: float = 0.70,
) -> List[Dict[str, Any]]:
    """Apply LLM fallback to a list of examples."""
    return [
        attach_llm_fallback(example, llm_judge=llm_judge, confidence_min=confidence_min, confidence_max=confidence_max)
        for example in examples
    ]


def process_stage8(
    input_path: str | Path,
    output_path: str | Path,
    llm_provider: str = "ollama",
    llm_model: str = "llama2",
    confidence_min: float = 0.40,
    confidence_max: float = 0.70,
) -> List[Dict[str, Any]]:
    """Load verified examples, apply LLM fallback where needed, and save results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    llm_judge = LLMJudge(provider=llm_provider, model=llm_model)
    processed_examples = apply_llm_fallback_to_examples(
        examples,
        llm_judge=llm_judge,
        confidence_min=confidence_min,
        confidence_max=confidence_max,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(processed_examples, handle, indent=2)

    return processed_examples
