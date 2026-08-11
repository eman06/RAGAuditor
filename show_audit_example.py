"""
Display a detailed example of an audit report with full formatting
"""

import json

# Load output
with open('data/processed/audit_reports.json', 'r') as f:
    reports = json.load(f)

# Find a report with some supported claims for better example
example_report = None
for report in reports:
    if report['audit_report']['summary']['supported_count'] > 0:
        example_report = report
        break

if not example_report:
    example_report = reports[0]

# Display formatted report
print("\n" + "=" * 100)
print("COMPLETE AUDIT REPORT EXAMPLE")
print("=" * 100)

print(f"\n📋 QUESTION:\n{example_report['question']}\n")
print(f"📝 ANSWER:\n{example_report['answer']}\n")

audit = example_report['audit_report']
summary = audit['summary']

print("=" * 100)
print("AUDIT REPORT")
print("=" * 100)

# Print summary header
print(f"\n🔴 {audit['explanation']}\n")

# Print claims
print("=" * 100)
print("CLAIM-BY-CLAIM VERIFICATION ANALYSIS")
print("=" * 100)

for idx, claim in enumerate(audit['claim_details'], 1):
    label = claim['verification_label']
    confidence = claim['confidence']
    
    # Symbol based on label
    if label == 'SUPPORTED':
        symbol = '✅'
    elif label == 'UNSUPPORTED':
        symbol = '❌'
    elif label == 'CONTRADICTED':
        symbol = '⚠️ '
    else:
        symbol = '❓'
    
    print(f"\n[Claim {idx}] {symbol} {label} (confidence: {confidence:.1%})")
    print(f"  Claim Text: \"{claim['claim']}\"")
    
    if claim['retrieved_evidence']:
        print(f"  Retrieved Evidence ({len(claim['retrieved_evidence'])} pieces):")
        for ev_idx, evidence in enumerate(claim['retrieved_evidence'], 1):
            print(f"    {ev_idx}. {evidence}")
    else:
        print(f"  Retrieved Evidence: None")
    
    print(f"  Explanation: {claim['explanation']}")

print("\n" + "=" * 100)
print(f"📊 STATISTICS")
print("=" * 100)
print(f"Total Claims: {summary['total_claims']}")
print(f"  ✅ Supported: {summary['supported_count']} ({summary['supported_count']/summary['total_claims']*100:.1f}%)")
print(f"  ❌ Unsupported: {summary['unsupported_count']} ({summary['unsupported_count']/summary['total_claims']*100:.1f}%)")
print(f"  ⚠️  Contradicted: {summary['contradicted_count']} ({summary['contradicted_count']/summary['total_claims']*100:.1f}%)")
print(f"  🔄 Partially Supported: {summary['partially_supported_count']} ({summary['partially_supported_count']/summary['total_claims']*100:.1f}%)")

print(f"\n🎯 HALLUCINATION RISK")
print(f"  Risk Score: {summary['risk_score']:.3f}")
print(f"  Risk Level: {summary['risk_level']}")

print("\n" + "=" * 100)
