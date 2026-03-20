## AI Healthcare Intelligence Engine 
Three connected backend modules exposed via FastAPI and demoed in Streamlit:

- **Symptom → Specialist Matching**: embedding-based similarity search over a (demo) case corpus.
- **Second Opinion Risk Stratifier**: rule-based MVP with explainable contributing phrases (upgradeable to a classifier).
- **Drug Interaction Intelligence**: knowledge-graph backed DDI lookup with severity and mechanism.

### Local setup

Use Python **3.12** (recommended) inside a virtual environment.

```bash
cd ai-healthcare-intel-engine
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
```

### Run the backend API

```bash
cd ai-healthcare-intel-engine
source .venv312/bin/activate
uvicorn api.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

### Run the Streamlit demo

```bash
cd ai-healthcare-intel-engine
source .venv312/bin/activate
cd frontend
streamlit run app.py
```

UI: `http://localhost:8501`

### Data pipeline hooks (optional)

These scripts let you convert external CSVs into the internal JSON formats used by the demo services:

```bash
python -m services.symptom_specialist.prepare_external_symptoms
python -m services.second_opinion.prepare_external_risk
python -m services.drug_interaction.prepare_external_ddi
```

Raw external datasets are intentionally ignored by git under `data/external/`.
Use the `*.example.csv` templates and copy them to the non-example filenames.

