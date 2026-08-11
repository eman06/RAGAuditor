from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover
    pipeline = None


class SimpleNLIVerifier:
    """A lightweight NLI-based claim verifier using a pre-trained model."""

    def __init__(self, model_name: str = "roberta-large-mnli") -> None:
        self.model_name = model_name
        self._classifier = None
        if pipeline is not None:
            try:
                self._classifier = pipeline("zero-shot-classification", model=model_name)
            except Exception:
                self._classifier = None

    def verify(
        self,
        claim: str,
        evidence: str,
        question: str = "",
        use_binary: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify if evidence supports a claim.
        
        Returns:
            {
                "label": "SUPPORTED" | "UNSUPPORTED" | "CONTRADICTED" | "PARTIALLY_SUPPORTED",
                "confidence": float between 0 and 1,
                "reasoning": str (optional)
            }
        """
        if not claim or not evidence:
            return {"label": "UNSUPPORTED", "confidence": 0.0}

        if self._classifier is not None:
            try:
                result = self._classifier(evidence, [claim])
                scores = result.get("scores", [])
                top_label = result.get("labels", ["UNSUPPORTED"])[0]

                if use_binary:
                    if "entailment" in top_label.lower() or scores[0] > 0.7:
                        return {"label": "SUPPORTED", "confidence": round(scores[0], 3)}
                    else:
                        return {"label": "UNSUPPORTED", "confidence": round(1.0 - scores[0], 3)}
                else:
                    if "entailment" in top_label.lower():
                        return {"label": "SUPPORTED", "confidence": round(scores[0], 3)}
                    elif "contradiction" in top_label.lower():
                        return {"label": "CONTRADICTED", "confidence": round(scores[0], 3)}
                    else:
                        return {"label": "UNSUPPORTED", "confidence": round(scores[0], 3)}
            except Exception:
                pass

        return self._fallback_verify(claim, evidence, use_binary=use_binary)

    def _fallback_verify(self, claim: str, evidence: str, use_binary: bool = True) -> Dict[str, Any]:
        """Simple fallback verifier based on token overlap."""
        claim_tokens = set(word.lower() for word in claim.split())
        evidence_tokens = set(word.lower() for word in evidence.split())

        overlap = claim_tokens & evidence_tokens
        overlap_ratio = len(overlap) / max(1, len(claim_tokens))

        if overlap_ratio > 0.6:
            return {"label": "SUPPORTED", "confidence": round(overlap_ratio, 3)}
        else:
            return {"label": "UNSUPPORTED", "confidence": round(1.0 - overlap_ratio, 3)}


def verify_claim(
    claim: str,
    evidence: str,
    question: str = "",
    verifier: Optional[SimpleNLIVerifier] = None,
    use_binary: bool = True,
) -> Dict[str, Any]:
    """Verify a single claim against evidence."""
    if verifier is None:
        verifier = SimpleNLIVerifier()
    return verifier.verify(claim, evidence, question=question, use_binary=use_binary)


def attach_claim_verification(
    example: Dict[str, Any],
    verifier: Optional[SimpleNLIVerifier] = None,
    use_binary: bool = True,
) -> Dict[str, Any]:
    """Attach verification results to each claim in an example."""
    example = dict(example)
    claims = example.get("claims", [])
    question = example.get("question", "")
    if verifier is None:
        verifier = SimpleNLIVerifier()

    enriched_claims = []
    for claim in claims:
        if isinstance(claim, dict):
            claim_text = claim.get("decontextualized_text") or claim.get("text", "")
            top_evidence = claim.get("top_evidence", [])

            if top_evidence:
                evidence_text = top_evidence[0].get("span", "")
                verification_result = verify_claim(
                    claim_text,
                    evidence_text,
                    question=question,
                    verifier=verifier,
                    use_binary=use_binary,
                )
            else:
                verification_result = {"label": "UNSUPPORTED", "confidence": 0.0}

            updated_claim = dict(claim)
            updated_claim["verification"] = verification_result
            enriched_claims.append(updated_claim)
        else:
            enriched_claims.append(claim)

    example["claims"] = enriched_claims
    return example


def verify_examples(
    examples: List[Dict[str, Any]],
    use_binary: bool = True,
) -> List[Dict[str, Any]]:
    """Apply claim verification to a list of examples."""
    verifier = SimpleNLIVerifier()
    return [attach_claim_verification(example, verifier=verifier, use_binary=use_binary) for example in examples]


def process_stage7(
    input_path: str | Path,
    output_path: str | Path,
    use_binary: bool = True,
) -> List[Dict[str, Any]]:
    """Load retrieval results, verify claims, and save the output."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    verified_examples = verify_examples(examples, use_binary=use_binary)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(verified_examples, handle, indent=2)

    return verified_examples
