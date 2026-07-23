# Deployment

## Recommended Deployment

Use Streamlit Cloud for the portfolio demo.

Settings:

- Repository: `shreyshrivastava/ai-healthcare-intel-engine`
- Branch: `streamlit-cloud` currently; `main` after merge
- Main file path: `ai-healthcare-intel-engine/frontend/app.py`
- Environment:
  - `HEALTHCARE_FRONTEND_MODE=local`
  - `HEALTHCARE_EMBEDDING_BACKEND=keyword`

This deploys one process and does not require FastAPI, GPUs, paid APIs, model downloads, or private credentials.

## Docker Deployment

Standalone Streamlit image:

```bash
docker build -t healthcare-intel-streamlit .
docker run --rm -p 8501:8501 healthcare-intel-streamlit
```

FastAPI image:

```bash
docker build -f Dockerfile.api -t healthcare-intel-api .
docker run --rm -p 8000:8000 healthcare-intel-api
```

Local multi-container demo:

```bash
docker compose up --build
```

## API Mode

For a full-stack demo, deploy FastAPI separately and set:

```bash
HEALTHCARE_FRONTEND_MODE=api
API_URL=https://your-api-host.example.com
```

Suitable API hosts include Render, Railway, Fly.io, or a Docker-based service.

## Health Check

FastAPI exposes:

```text
/health
```

Metrics snapshot:

```text
/metrics
```

## Current Live URL

Verified Streamlit Cloud URL:

```text
https://healthcare-intel-engine-shrey.streamlit.app/
```

The live app was tested in deterministic standalone mode and in a fresh browser profile without existing Streamlit cookies.

## Manual Steps Remaining

1. Merge the upgrade branch into `main`.
2. Update the Streamlit Cloud app from `streamlit-cloud` to `main` after merge, or keep `streamlit-cloud` as the deployment branch.
