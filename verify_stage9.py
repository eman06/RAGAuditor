import json

with open('data/processed/ragtruth_risk_aggregation.json', 'r') as f:
    data = json.load(f)
    example = data[0]
    
    print('Answer risk structure:')
    risk = example.get('answer_risk', {})
    for key, value in risk.items():
        if key != 'metrics':
            print(f'  {key}: {value}')
    
    print('\nDetailed metrics:')
    metrics = risk.get('metrics', {})
    for key, value in metrics.items():
        print(f'  {key}: {value}')
