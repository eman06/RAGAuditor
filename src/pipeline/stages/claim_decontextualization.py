from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence


def build_decontextualization_prompt(question: str, sentence: str, claim: str) -> str:
    """Build the prompt used to rewrite a claim into a self-contained form."""
    return (
        "You are given a question, an answer sentence, and an extracted claim.\n"
        "Rewrite the claim so it is self-contained.\n"
        "Do not add new information.\n"
        "Do not change the meaning.\n"
        "Return only the rewritten claim.\n\n"
        f"Question:\n{question}\n\n"
        f"Answer sentence:\n{sentence}\n\n"
        f"Claim:\n{claim}"
    )


def decontextualize_claim(
    claim: str,
    question: str,
    sentence: str,
    llm_client: Optional[Callable[[str], str]] = None,
) -> str:
    """Rewrite a claim so it is self-contained, using an LLM when available."""
    clean_claim = claim.strip()
    if not clean_claim:
        return ""

    if llm_client is not None:
        try:
            rewritten = llm_client(build_decontextualization_prompt(question, sentence, clean_claim)).strip()
            if rewritten:
                return rewritten
        except Exception:
            pass

    if clean_claim.lower().startswith(("it ", "they ", "he ", "she ")):
        return f"{sentence}"

    return clean_claim


def decontextualize_example(
    example: Dict[str, Any],
    llm_client: Optional[Callable[[str], str]] = None,
) -> Dict[str, Any]:
    """Rewrite all claims in an example into self-contained claims."""
    example = dict(example)
    claims = example.get("claims", [])
    rewritten_claims = []
    for claim in claims:
        if isinstance(claim, dict):
            text = claim.get("text", "")
            rewritten = decontextualize_claim(
                text,
                example.get("question", ""),
                claim.get("source_sentence", ""),
                llm_client=llm_client,
            )
            updated_claim = dict(claim)
            updated_claim["decontextualized_text"] = rewritten
            rewritten_claims.append(updated_claim)
        else:
            rewritten_claims.append(claim)
    example["claims"] = rewritten_claims
    return example


def decontextualize_examples(
    examples: List[Dict[str, Any]],
    llm_client: Optional[Callable[[str], str]] = None,
) -> List[Dict[str, Any]]:
    """Apply decontextualization to a list of examples."""
    return [decontextualize_example(example, llm_client=llm_client) for example in examples]


def process_stage4(
    input_path: str | Path,
    output_path: str | Path,
    llm_client: Optional[Callable[[str], str]] = None,
) -> List[Dict[str, Any]]:
    """Load claim-decomposed examples, rewrite claims, and save the results."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as handle:
        examples = json.load(handle)

    decontextualized_examples = decontextualize_examples(examples, llm_client=llm_client)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(decontextualized_examples, handle, indent=2)

    return decontextualized_examples
