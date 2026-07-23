# Portfolio Project Audit

## Executive Summary

The project is now a credible supporting AI engineering portfolio project. Its strongest evidence is not model novelty; it is the practical engineering around safe healthcare AI demos: deterministic fallback, API validation, CI-safe tests, synthetic evaluation, model-comparison hooks, latency benchmarks, privacy documentation, observability, screenshots, and deployment readiness.

Initial estimated score: 4.2/10. Final estimated score after this pass: 8.0/10.

## Resume Decision

Supporting resume project.

It supports Applied AI Engineer, AI Engineer, LLM/GenAI Engineer, Machine Learning Engineer, AI Data Engineer, and Python Backend Engineer roles. It should not be positioned as a production healthcare product or clinically validated AI system.

## Best Target Roles

- Applied AI Engineer
- AI Engineer
- LLM Engineer
- Generative AI Engineer
- Machine Learning Engineer
- AI Data Engineer
- Python Backend Engineer

## Hiring-Manager Scores

| Category | Score |
| --- | ---: |
| Technical depth | 7 |
| Software engineering quality | 8 |
| AI/ML relevance | 7 |
| Product usefulness | 8 |
| Reliability | 8 |
| Documentation | 9 |
| Deployment readiness | 8 |
| Testing quality | 8 |
| Originality | 6 |
| Resume value | 8 |

## Strongest Evidence

- Three coherent healthcare workflows exposed through FastAPI and Streamlit.
- Deterministic keyword backend for CI/cloud plus optional sentence-transformer backend for local experiments.
- DDI lookup modeled as a graph with local medication alias normalization.
- Pydantic validation on API inputs.
- Synthetic evaluation and latency benchmarks committed as reproducible scripts.
- Privacy and clinical-safety limitations documented clearly.
- Streamlit screenshots captured from an actual local UI test run.

## Weaknesses

- Synthetic data is small and not clinically representative.
- Evaluation currently measures regression behavior, not real-world clinical accuracy.
- No public deployment has been verified yet.
- No durable monitoring, audit logging, authentication, or HIPAA-grade controls.
- DDI graph is not comprehensive.

## Changes Implemented

- Added deterministic symptom encoder fallback.
- Removed hard dependency on torch, transformers, sentence-transformers, FAISS, SHAP, and Captum from base requirements.
- Preserved optional sentence-transformer support in `requirements-ml.txt`.
- Replaced FAISS dependency with a lightweight NumPy cosine vector store.
- Added FastAPI validation and `/health`.
- Added standalone Streamlit mode for Streamlit Cloud.
- Improved second-opinion risk phrase matching and negation handling.
- Fixed DDI normalized generic lookup for levothyroxine/Synthroid.
- Added pytest suite, evaluation script, benchmark script, CI, benchmark workflow, README, docs, audit JSON, and MIT license.
- Added expanded synthetic evaluation cases, model-comparison script, API observability, Dockerfiles, and improved Streamlit UI.

## Tests

Latest local result:

```text
20 passed, 1 warning
```

The warning is from FastAPI/Starlette's test client dependency transition and does not affect runtime behavior.

## Evaluation

Latest local deterministic evaluation:

- Symptom specialist top-1 accuracy: 100.00% over 32 cases
- Symptom specialist top-3 accuracy: 100.00% over 32 cases
- Second-opinion risk accuracy: 100.00% over 32 cases
- DDI positive recall: 100.00% over 20 known interactions
- DDI expanded scenario accuracy: 100.00% over 5 alias/edge cases
- DDI negative specificity: 100.00% over 10 negative pairs

These are synthetic regression metrics, not clinical validation metrics.

## Benchmarks

Latest local deterministic benchmark:

- API app creation median: 0.14 ms
- Symptom ranking median: 0.03 ms
- Second-opinion risk median: 0.03 ms
- Drug interaction check median: 0.07 ms

Environment: Python 3.14.5 on macOS 26.5.2 arm64, keyword backend, 10 iterations.

## Deployment

Prepared for Streamlit Cloud standalone deployment.

Dockerfiles were added for Streamlit and FastAPI. Local Docker image builds were not run in this environment because the `docker` CLI is not installed.

## Live URL

No verified live URL yet.

## CI/CD

Added GitHub Actions CI and benchmark workflows.

CI runs dependency install, ruff linting, ruff formatting checks, compileall, pytest, evaluation, model-comparison smoke, benchmark smoke, and Docker build validation in deterministic keyword mode.

## Security and Privacy

- No credentials added.
- No real patient data added.
- Raw external datasets are ignored by git.
- README and UI warn against entering PHI.
- No external API calls in default mode.

## Resume Description

AI Healthcare Intelligence Engine: built a FastAPI and Streamlit clinical decision-support demo with deterministic symptom ranking, explainable risk stratification, DDI graph lookup, CI-safe evaluation, and deployment-ready fallback behavior.

## Resume Bullets

- Built a three-module healthcare AI demo with FastAPI endpoints and a Streamlit UI for symptom-specialist routing, second-opinion risk, and drug-drug interaction lookup.
- Added deterministic CI/cloud fallback for symptom ranking while preserving optional sentence-transformer embeddings for local ML experimentation.
- Implemented API validation, graph-based DDI lookup, RxNorm-style alias normalization, synthetic evaluation, model comparison, latency benchmarks, observability, Docker, and GitHub Actions CI.
- Documented privacy, healthcare safety boundaries, deployment tradeoffs, and limitations to avoid unsupported clinical claims.

## Remaining Limitations

- Needs public Streamlit deployment.
- Needs larger licensed datasets before stronger ML quality claims.
- Needs real observability and auth before any production-like healthcare positioning.

## Recommended Next Step

Push this branch, open a PR, verify GitHub Actions, then deploy the Streamlit app in local deterministic mode.
