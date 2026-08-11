"""
Stage 10: Audit Report Generation

Generates human-readable audit reports for each answer, including:
- Answer-level risk summary (risk score, risk level, claim counts)
- Claim-by-claim evidence breakdown
- Explanations for unsupported/contradicted claims
- Detailed reasoning

Input: ragtruth_risk_aggregation.json (from Stage 9)
Output: audit_reports.json (human-readable reports)
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def generate_claim_explanation(claim_data: Dict[str, Any], evidence_data: Dict[str, Any]) -> str:
    """
    Generate explanation for claim's verification result.
    
    Args:
        claim_data: Claim with verification result
        evidence_data: Retrieved evidence and evaluation
    
    Returns:
        String explanation of verification result
    """
    label = claim_data.get('verification', {}).get('label', 'UNKNOWN')
    evidence = evidence_data.get('top_evidence', [])
    confidence = claim_data.get('verification', {}).get('confidence', 0.0)
    
    if not evidence:
        return f"No retrieved evidence available to verify this claim."
    
    evidence_texts = [ev.get('span', '') for ev in evidence if ev.get('span')]
    evidence_str = " | ".join(evidence_texts[:3]) if evidence_texts else "No evidence"
    
    if label == 'SUPPORTED':
        return f"Evidence found that supports this claim: '{evidence_str}'"
    elif label == 'UNSUPPORTED':
        return f"No retrieved evidence supports this claim. Retrieved evidence: '{evidence_str}'"
    elif label == 'CONTRADICTED':
        return f"Retrieved evidence contradicts this claim: '{evidence_str}'"
    elif label == 'PARTIALLY_SUPPORTED':
        return f"Retrieved evidence only partially supports this claim: '{evidence_str}'"
    else:
        return f"Verification status unknown (confidence: {confidence:.3f})"


def generate_answer_explanation(risk_data: Dict[str, Any], claims: List[Dict[str, Any]]) -> str:
    """
    Generate summary explanation of answer's hallucination risk.
    
    Args:
        risk_data: Answer-level risk aggregation
        claims: List of claims for this answer
    
    Returns:
        Summary explanation string
    """
    total = risk_data.get('total_claims', 0)
    supported = risk_data.get('supported_count', 0)
    unsupported = risk_data.get('unsupported_count', 0)
    contradicted = risk_data.get('contradicted_count', 0)
    partial = risk_data.get('partial_support_count', 0)
    risk_level = risk_data.get('risk_level', 'UNKNOWN')
    risk_score = risk_data.get('risk_score', 0.0)
    
    if total == 0:
        return "Answer contains no extractable claims."
    
    # Build summary statement
    summary = f"Risk Level: {risk_level}\n"
    summary += f"\nThe answer contains {total} claim{'s' if total != 1 else ''}.\n"
    summary += f"{supported} {'is' if supported == 1 else 'are'} supported.\n"
    
    if unsupported > 0:
        summary += f"{unsupported} {'is' if unsupported == 1 else 'are'} unsupported.\n"
    if contradicted > 0:
        summary += f"{contradicted} {'is' if contradicted == 1 else 'are'} contradicted.\n"
    if partial > 0:
        summary += f"{partial} {'is' if partial == 1 else 'are'} partially supported.\n"
    
    summary += f"\nHallucination Risk Score: {risk_score:.3f} ({risk_level})"
    
    return summary


def generate_claim_report(claim_text: str, claim_data: Dict[str, Any], 
                         evidence_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate report entry for a single claim.
    
    Args:
        claim_text: The claim text
        claim_data: Claim verification result
        evidence_data: Retrieved evidence for this claim
    
    Returns:
        Dictionary with claim details
    """
    verification = claim_data.get('verification', {})
    label = verification.get('label', 'UNKNOWN')
    confidence = verification.get('confidence', 0.0)
    evidence_list = evidence_data.get('top_evidence', [])
    
    # Extract evidence texts
    evidence_texts = [ev.get('span', '') for ev in evidence_list if ev.get('span')][:5]
    
    # Generate explanation
    explanation = generate_claim_explanation(claim_data, evidence_data)
    
    return {
        'claim': claim_text,
        'verification_label': label,
        'confidence': float(confidence),
        'retrieved_evidence': evidence_texts,
        'explanation': explanation
    }


def generate_audit_report(example: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete audit report for an answer.
    
    Args:
        example: Processed example with all stages completed
    
    Returns:
        Dictionary with audit report
    """
    # Extract components
    answer_risk = example.get('answer_risk', {})
    claims = example.get('claims', [])
    
    # Generate summary
    summary = {
        'risk_score': float(answer_risk.get('risk_score', 0.0)),
        'risk_level': answer_risk.get('risk_level', 'UNKNOWN'),
        'total_claims': answer_risk.get('total_claims', 0),
        'supported_count': answer_risk.get('supported_count', 0),
        'unsupported_count': answer_risk.get('unsupported_count', 0),
        'contradicted_count': answer_risk.get('contradicted_count', 0),
        'partially_supported_count': answer_risk.get('partial_support_count', 0)
    }
    
    # Generate overall explanation
    explanation = generate_answer_explanation(answer_risk, claims)
    
    # Generate claim-by-claim details
    claim_details = []
    for claim_data in claims:
        claim_text = claim_data.get('text', 'Unknown claim')
        evidence_data = claim_data.get('evidence_retrieval', {})
        
        claim_report = generate_claim_report(claim_text, claim_data, evidence_data)
        claim_details.append(claim_report)
    
    # Sort by verification label (unsupported/contradicted first for easier scanning)
    label_order = {'UNSUPPORTED': 0, 'CONTRADICTED': 1, 'PARTIALLY_SUPPORTED': 2, 'SUPPORTED': 3, 'UNKNOWN': 4}
    claim_details.sort(key=lambda x: label_order.get(x.get('verification_label', 'UNKNOWN'), 5))
    
    return {
        'summary': summary,
        'explanation': explanation,
        'claim_details': claim_details
    }


def process_stage10(input_file: str = 'data/processed/ragtruth_risk_aggregation.json',
                   output_file: str = 'data/processed/audit_reports.json') -> Dict[str, Any]:
    """
    Process Stage 10: Generate audit reports for all answers.
    
    Args:
        input_file: Path to input JSON (from Stage 9)
        output_file: Path to output JSON (audit reports)
    
    Returns:
        Dictionary with processing statistics
    """
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Load input data
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Process each example
    reports = []
    stats = {
        'total_processed': 0,
        'total_claims': 0,
        'supported_total': 0,
        'unsupported_total': 0,
        'contradicted_total': 0,
        'partial_support_total': 0,
        'risk_level_distribution': {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'CRITICAL': 0,
            'UNKNOWN': 0
        }
    }
    
    for example in data:
        try:
            audit_report = generate_audit_report(example)
            
            # Add metadata
            report_entry = {
                'id': example.get('id', ''),
                'question': example.get('question', ''),
                'answer': example.get('answer', ''),
                'audit_report': audit_report
            }
            reports.append(report_entry)
            
            # Update statistics
            summary = audit_report['summary']
            stats['total_processed'] += 1
            stats['total_claims'] += summary['total_claims']
            stats['supported_total'] += summary['supported_count']
            stats['unsupported_total'] += summary['unsupported_count']
            stats['contradicted_total'] += summary['contradicted_count']
            stats['partial_support_total'] += summary['partially_supported_count']
            
            risk_level = summary['risk_level']
            if risk_level in stats['risk_level_distribution']:
                stats['risk_level_distribution'][risk_level] += 1
            else:
                stats['risk_level_distribution']['UNKNOWN'] += 1
                
        except Exception as e:
            print(f"Error processing example {example.get('id', 'unknown')}: {e}")
            continue
    
    # Save reports
    with open(output_path, 'w') as f:
        json.dump(reports, f, indent=2)
    
    # Add output path to stats
    stats['output_file'] = str(output_path)
    stats['examples_processed'] = len(reports)
    
    return stats


if __name__ == '__main__':
    print("Running Stage 10: Audit Report Generation...")
    stats = process_stage10()
    
    print(f"\n✓ Processed {stats['examples_processed']} examples")
    print(f"✓ Generated {stats['examples_processed']} audit reports")
    print(f"\nClaim Statistics:")
    print(f"  Total claims: {stats['total_claims']}")
    print(f"  Supported: {stats['supported_total']}")
    print(f"  Unsupported: {stats['unsupported_total']}")
    print(f"  Contradicted: {stats['contradicted_total']}")
    print(f"  Partially Supported: {stats['partial_support_total']}")
    
    print(f"\nRisk Level Distribution:")
    for level, count in stats['risk_level_distribution'].items():
        pct = (count / stats['examples_processed'] * 100) if stats['examples_processed'] > 0 else 0
        print(f"  {level}: {count} ({pct:.1f}%)")
    
    print(f"\nOutput saved to: {stats['output_file']}")
