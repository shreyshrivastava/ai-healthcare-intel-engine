# Technical Decisions

## Deterministic Default

The default symptom encoder is keyword-based. This keeps CI and Streamlit Cloud reliable and avoids surprise model downloads.

## Optional ML Backend

Sentence-transformers are preserved as an optional local backend through `requirements-ml.txt` and `HEALTHCARE_EMBEDDING_BACKEND=sentence-transformer`.

## Standalone Streamlit Mode

The frontend defaults to local service calls so Streamlit Cloud can host the demo without a separate FastAPI server.

## API Mode Preserved

FastAPI is still useful for backend engineering evidence, API docs, validation, and future full-stack deployment. The frontend can call it with `HEALTHCARE_FRONTEND_MODE=api`.

## Synthetic Metrics

Evaluation and benchmark outputs are saved, but the README labels them as synthetic regression evidence instead of clinical accuracy.
