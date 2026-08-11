"""
Run Stage 10: Audit Report Generation on full dataset
"""

from src.pipeline.stages.audit_report_generation import process_stage10

if __name__ == '__main__':
    print("=" * 60)
    print("STAGE 10: AUDIT REPORT GENERATION")
    print("=" * 60)
    
    stats = process_stage10()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Examples: {stats['examples_processed']}")
    print(f"Audit Reports Generated: {stats['examples_processed']}")
    
    print(f"\n{'-' * 60}")
    print("CLAIM STATISTICS")
    print(f"{'-' * 60}")
    print(f"Total Claims Analyzed: {stats['total_claims']}")
    print(f"  Supported: {stats['supported_total']}")
    print(f"  Unsupported: {stats['unsupported_total']}")
    print(f"  Contradicted: {stats['contradicted_total']}")
    print(f"  Partially Supported: {stats['partial_support_total']}")
    
    print(f"\n{'-' * 60}")
    print("RISK LEVEL DISTRIBUTION")
    print(f"{'-' * 60}")
    for level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
        count = stats['risk_level_distribution'].get(level, 0)
        pct = (count / stats['examples_processed'] * 100) if stats['examples_processed'] > 0 else 0
        print(f"{level:10s}: {count:6d} ({pct:5.1f}%)")
    
    print(f"\n{'-' * 60}")
    print(f"Output File: {stats['output_file']}")
    print(f"{'-' * 60}")
