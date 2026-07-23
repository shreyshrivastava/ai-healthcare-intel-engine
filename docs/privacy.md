# Privacy

## Data Processed

The app processes user-entered symptom text, de-identified report summaries, and medication names.

## Data Stored

The app does not intentionally store user-entered text. Demo datasets in `ai-healthcare-intel-engine/data/demo/` are synthetic.

## External Data

`ai-healthcare-intel-engine/data/external/` is intended for user-downloaded datasets. Raw CSV, Parquet, and ZIP files are ignored by git. Only small example templates are tracked.

## External Services

Default mode uses no external APIs and no LLM calls.

Optional sentence-transformer mode may download a public model when enabled locally. Do not enable it in low-resource public demos unless you have tested memory, cold-start, and privacy expectations.

## PHI Guidance

Do not paste names, dates of birth, addresses, medical record numbers, phone numbers, emails, or other protected health information into a public deployment.

The project is not HIPAA-compliant as-is and should not be marketed as such.
