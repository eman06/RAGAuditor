"""
Test file for Stage 10: Audit Report Generation
"""

import json
import pytest
from pathlib import Path
from src.pipeline.stages.audit_report_generation import (
    generate_claim_explanation,
    generate_answer_explanation,
    generate_claim_report,
    generate_audit_report
)


def test_generate_claim_explanation_supported():
    """Test explanation generation for supported claims."""
    claim_data = {
        'verification': {
            'label': 'SUPPORTED',
            'confidence': 0.85
        }
    }
    evidence_data = {
        'top_evidence': [
            {'span': 'The company raised $20M in Series A'},
            {'span': 'Funding announcement confirmed'}
        ]
    }
    
    explanation = generate_claim_explanation(claim_data, evidence_data)
    assert 'supports this claim' in explanation
    assert 'Series A' in explanation


def test_generate_claim_explanation_unsupported():
    """Test explanation generation for unsupported claims."""
    claim_data = {
        'verification': {
            'label': 'UNSUPPORTED',
            'confidence': 0.72
        }
    }
    evidence_data = {
        'top_evidence': [
            {'span': 'Company was founded in 2018'},
            {'span': 'HQ is in San Francisco'}
        ]
    }
    
    explanation = generate_claim_explanation(claim_data, evidence_data)
    assert 'No retrieved evidence supports' in explanation


def test_generate_claim_explanation_contradicted():
    """Test explanation generation for contradicted claims."""
    claim_data = {
        'verification': {
            'label': 'CONTRADICTED',
            'confidence': 0.82
        }
    }
    evidence_data = {
        'top_evidence': [
            {'span': 'Company has 500 employees, not 1000'}
        ]
    }
    
    explanation = generate_claim_explanation(claim_data, evidence_data)
    assert 'contradicts this claim' in explanation


def test_generate_answer_explanation():
    """Test overall answer explanation generation."""
    risk_data = {
        'total_claims': 5,
        'supported_count': 3,
        'unsupported_count': 1,
        'contradicted_count': 1,
        'partial_support_count': 0,
        'risk_level': 'HIGH',
        'risk_score': 0.68
    }
    claims = [
        {'text': 'Claim 1'},
        {'text': 'Claim 2'},
        {'text': 'Claim 3'},
        {'text': 'Claim 4'},
        {'text': 'Claim 5'}
    ]
    
    explanation = generate_answer_explanation(risk_data, claims)
    assert 'Risk Level: HIGH' in explanation
    assert '5 claims' in explanation
    assert '3 are supported' in explanation
    assert '1 is unsupported' in explanation
    assert '1 is contradicted' in explanation


def test_generate_claim_report():
    """Test single claim report generation."""
    claim_text = "The company raised $20M in Series A funding."
    claim_data = {
        'verification': {
            'label': 'SUPPORTED',
            'confidence': 0.857
        }
    }
    evidence_data = {
        'top_evidence': [
            {'span': '$20M Series A funding announcement'},
            {'span': 'Investment round completed'}
        ]
    }
    
    report = generate_claim_report(claim_text, claim_data, evidence_data)
    
    assert report['claim'] == claim_text
    assert report['verification_label'] == 'SUPPORTED'
    assert report['confidence'] == 0.857
    assert len(report['retrieved_evidence']) == 2
    assert 'Series A' in report['retrieved_evidence'][0]


def test_generate_audit_report():
    """Test full audit report generation."""
    example = {
        'id': 'test_123',
        'question': 'When was the company founded?',
        'answer': 'The company was founded in 2015 and raised $20M in Series A.',
        'answer_risk': {
            'risk_score': 0.481,
            'risk_level': 'MEDIUM',
            'total_claims': 2,
            'supported_count': 1,
            'unsupported_count': 1,
            'contradicted_count': 0,
            'partial_support_count': 0
        },
        'claims': [
            {
                'text': 'The company was founded in 2015.',
                'verification': {
                    'label': 'SUPPORTED',
                    'confidence': 0.91
                },
                'evidence_retrieval': {
                    'top_evidence': [
                        {'span': 'Company founding date: 2015'}
                    ]
                }
            },
            {
                'text': 'The company raised $20M in Series A.',
                'verification': {
                    'label': 'UNSUPPORTED',
                    'confidence': 0.68
                },
                'evidence_retrieval': {
                    'top_evidence': [
                        {'span': 'No funding information available'}
                    ]
                }
            }
        ]
    }
    
    report = generate_audit_report(example)
    
    # Check summary
    assert report['summary']['risk_score'] == 0.481
    assert report['summary']['risk_level'] == 'MEDIUM'
    assert report['summary']['total_claims'] == 2
    assert report['summary']['supported_count'] == 1
    assert report['summary']['unsupported_count'] == 1
    
    # Check explanation
    assert 'Risk Level: MEDIUM' in report['explanation']
    
    # Check claim details
    assert len(report['claim_details']) == 2
    # Unsupported claims should come first (sorted by label)
    assert report['claim_details'][0]['verification_label'] == 'UNSUPPORTED'
    assert report['claim_details'][1]['verification_label'] == 'SUPPORTED'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
