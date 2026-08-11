import json

with open('data/processed/ragtruth_llm_fallback.json', 'r') as f:
    data = json.load(f)
    example = data[0]
    claim = None
    # Find a claim with LLM fallback
    for c in example['claims']:
        if 'llm_fallback' in c:
            claim = c
            break
    if claim:
        print('Claim with LLM fallback:')
        print(f"  Text: {claim.get('text', '')[:50]}...")
        print(f"  Verification label: {claim.get('verification', {}).get('label')}")
        print(f"  Verification confidence: {claim.get('verification', {}).get('confidence')}")
        print(f"  LLM Fallback label: {claim.get('llm_fallback', {}).get('label')}")
        print(f"  LLM Fallback reason: {claim.get('llm_fallback', {}).get('reason')}")
    else:
        print('Sample claim (no LLM fallback):')
        claim = example['claims'][0]
        print(f"  Verification: {claim.get('verification', {})}")
        print(f"  Has llm_fallback: {'llm_fallback' in claim}")
