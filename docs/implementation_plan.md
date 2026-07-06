# Implementation plan for two people

## Person 1: Pipeline and claim decomposition
Responsibilities:
- Set up the project structure and configuration.
- Implement data loading and example normalization.
- Implement sentence segmentation.
- Implement selective claim decomposition logic.
- Implement claim decontextualization.
- Implement evidence unit creation.
- Connect the stages into a simple end-to-end pipeline.

Deliverables:
- A working preprocessing pipeline that turns raw examples into claims.
- Unit tests for sentence splitting and decomposition.
- A clear interface for passing claims into the verification stage.

## Person 2: Retrieval, verification, and reporting
Responsibilities:
- Implement evidence-span retrieval using BM25 and dense embeddings.
- Implement claim verification with a compact baseline model.
- Add uncertainty-based LLM fallback logic.
- Implement answer-level risk aggregation.
- Build audit report generation.
- Run evaluation on benchmark datasets and compare results.

Deliverables:
- A verification pipeline that outputs claim labels and confidence.
- Risk scoring and report generation.
- Evaluation scripts and basic metrics.

## Suggested weekly workflow
- Week 1: Build shared schema and stage interfaces.
- Week 2: Complete Person 1 modules.
- Week 3: Complete Person 2 modules.
- Week 4: Integration, evaluation, and polishing.
