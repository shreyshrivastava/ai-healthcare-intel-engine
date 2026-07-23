# Limitations

- This is not a medical device.
- This is not medical advice.
- Demo data is synthetic and small.
- Evaluation reuses synthetic/demo data, so metrics are regression evidence rather than clinical generalization evidence.
- The keyword encoder is deterministic and deployment-friendly but less semantically rich than a clinical embedding model.
- Optional sentence-transformer mode requires model download and more memory.
- The DDI graph is a small curated demo graph, not a complete drug database.
- Risk stratification is rule-based and should not be used for real triage.
- No authentication, audit trail, durable storage, HIPAA controls, or monitoring are implemented.

## Recommended Next Improvements

- Add a larger public benchmark dataset with clear licensing.
- Add calibrated confidence bands and abstention behavior.
- Add Docker deployment for the FastAPI backend.
- Add screenshots after a public demo is deployed.
- Add observability for API latency and error rates.
