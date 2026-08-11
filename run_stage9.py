from src.pipeline.stages.answer_risk_aggregation import process_stage9
import json

result = process_stage9('data/processed/ragtruth_llm_fallback.json', 'data/processed/ragtruth_risk_aggregation.json')
print(f'Processed {len(result)} examples')

# Analyze risk distribution
risk_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
for example in result:
    risk_level = example.get('answer_risk', {}).get('risk_level')
    if risk_level in risk_distribution:
        risk_distribution[risk_level] += 1

print(f'\nRisk level distribution:')
for level, count in risk_distribution.items():
    percentage = (count / len(result)) * 100
    print(f'  {level}: {count} ({percentage:.1f}%)')

# Show example
if result:
    example = result[0]
    risk = example.get('answer_risk', {})
    print(f'\nExample answer risk:')
    print(f"  Risk score: {risk.get('risk_score')}")
    print(f"  Risk level: {risk.get('risk_level')}")
    print(f"  Total claims: {risk.get('total_claims')}")
    print(f"  Supported: {risk.get('supported_count')}")
    print(f"  Unsupported: {risk.get('unsupported_count')}")
    print(f"  Contradicted: {risk.get('contradicted_count')}")
    print(f"  Average confidence: {risk.get('average_confidence')}")

print('\nStage 9 complete!')
