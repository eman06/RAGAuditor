from src.pipeline.stages.claim_llm_fallback import apply_llm_fallback_to_examples
import json
from pathlib import Path

# Load verified examples
with open('data/processed/ragtruth_verified.json', 'r') as f:
    examples = json.load(f)

# Mock LLM judge that doesn't require external service
class MockLLMJudge:
    def judge(self, question, claim, evidence):
        # Simple mock that returns extended labels
        if len(claim) > 50:
            return {"label": "PARTIALLY_SUPPORTED", "reason": "Long claim may be partially supported."}
        return {"label": "SUPPORTED", "reason": "Mock judgment."}

mock_judge = MockLLMJudge()

# Apply LLM fallback
processed_examples = apply_llm_fallback_to_examples(
    examples,
    llm_judge=mock_judge,
    confidence_min=0.40,
    confidence_max=0.70
)

# Count how many claims got LLM fallback
llm_fallback_count = 0
for example in processed_examples:
    for claim in example.get('claims', []):
        if 'llm_fallback' in claim:
            llm_fallback_count += 1

print(f'Processed {len(processed_examples)} examples')
print(f'Claims with LLM fallback: {llm_fallback_count}')

# Save results
output_path = Path('data/processed/ragtruth_llm_fallback.json')
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open('w', encoding='utf-8') as f:
    json.dump(processed_examples, f, indent=2)

print(f'Results saved to: {output_path}')

# Show example
if processed_examples:
    first_claim = processed_examples[0]['claims'][0]
    print(f'\nExample claim:')
    print(f"  Verification: {first_claim.get('verification', {})}")
    if 'llm_fallback' in first_claim:
        print(f"  LLM Fallback: {first_claim.get('llm_fallback', {})}")
