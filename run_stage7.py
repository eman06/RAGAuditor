from src.pipeline.stages.claim_verification import process_stage7

result = process_stage7('data/processed/ragtruth_retrieval.json', 'data/processed/ragtruth_verified.json', use_binary=True)
print(f'Processed {len(result)} examples')
if result and result[0].get('claims'):
    verification = result[0]['claims'][0].get('verification', {})
    print(f'First claim verification label: {verification.get("label")}')
    print(f'First claim verification confidence: {verification.get("confidence")}')
    print('Stage 7 complete!')
