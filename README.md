# RAGAuditor

## Proposed project structure

```text
RAGAuditor/
├── data/
│   ├── raw/
│   ├── processed/
│   └── annotations/
├── docs/
│   ├── proposal.md
│   └── architecture.md
├── src/
│   ├── pipeline/
│   │   ├── stages/
│   │   │   ├── data_loading.py
│   │   │   ├── sentence_segmentation.py
│   │   │   ├── selective_decomposition.py
│   │   │   ├── claim_decontextualization.py
│   │   │   ├── evidence_unit_creation.py
│   │   │   ├── evidence_retrieval.py
│   │   │   ├── claim_verification.py
│   │   │   ├── llm_fallback.py
│   │   │   └── risk_aggregation.py
│   │   └── utils/
│   │       ├── preprocessing.py
│   │       ├── logging.py
│   │       └── config.py
│   ├── models/
│   │   ├── verifier.py
│   │   └── retrieval.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── benchmarks.py
│   └── main.py
├── tests/
│   ├── test_pipeline.py
│   └── test_evaluation.py
└── requirements.txt
```

## Suggested two-person implementation split

### Person 1: Claim processing and pipeline core
Focus on the front half of the pipeline:
- data loading and schema normalization
- sentence segmentation
- selective claim decomposition
- claim decontextualization
- evidence unit creation
- basic pipeline orchestration

### Person 2: Retrieval, verification, and evaluation
Focus on the backend and evaluation side:
- evidence retrieval with BM25 + dense embeddings
- claim verification and uncertainty-based LLM fallback
- answer-level risk aggregation
- evaluation metrics and dataset benchmarking
- reporting and experiment tracking

## Suggested milestone order
1. Build the data schema and pipeline skeleton.
2. Implement sentence splitting and selective decomposition.
3. Implement evidence retrieval and claim verification.
4. Add aggregation and evaluation metrics.
5. Run experiments on RAGTruth / AttributionBench.
