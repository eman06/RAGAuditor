"""
Verify Stage 10 output - display sample audit reports
"""

import json

# Load output
with open('data/processed/audit_reports.json', 'r') as f:
    reports = json.load(f)

if not reports:
    print("No reports found!")
    exit(1)

# Show first 3 reports
print("=" * 80)
print("AUDIT REPORT SAMPLES (First 3 Examples)")
print("=" * 80)

for idx, report in enumerate(reports[:3], 1):
    print(f"\n{'-' * 80}")
    print(f"REPORT #{idx}")
    print(f"{'-' * 80}")
    print(f"Question: {report.get('question', 'N/A')[:100]}...")
    print(f"Answer: {report.get('answer', 'N/A')[:100]}...")
    
    audit = report.get('audit_report', {})
    summary = audit.get('summary', {})
    
    print(f"\n{audit.get('explanation', 'N/A')}")
    
    print(f"\n{'Claim-by-Claim Analysis:':^80}")
    print("-" * 80)
    
    for claim_idx, claim in enumerate(audit.get('claim_details', [])[:5], 1):
        print(f"\nClaim {claim_idx}: {claim.get('claim', 'N/A')[:70]}...")
        print(f"  Verification: {claim.get('verification_label', 'UNKNOWN')} (confidence: {claim.get('confidence', 0.0):.3f})")
        
        evidence = claim.get('retrieved_evidence', [])
        if evidence:
            print(f"  Evidence Retrieved ({len(evidence)}):")
            for ev in evidence[:3]:
                print(f"    - {ev[:70]}...")
        else:
            print(f"  Evidence Retrieved: None")
        
        print(f"  Explanation: {claim.get('explanation', 'N/A')[:70]}...")
    
    if len(audit.get('claim_details', [])) > 5:
        print(f"\n  ... and {len(audit.get('claim_details', [])) - 5} more claims")

print(f"\n{'=' * 80}")
print(f"Total Reports Generated: {len(reports)}")
print(f"Output File: data/processed/audit_reports.json")
print(f"{'=' * 80}")
