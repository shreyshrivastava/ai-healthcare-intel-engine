# AI Healthcare Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)

End-to-end clinical intelligence platform for symptom-specialist matching, risk stratification, and drug interaction detection using vector embeddings, NLP, and NetworkX graph traversal.

## 🚀 Key Features

### 1. Symptom → Specialist Matching
Utlizes an NLP Engine utilizing a **sentence-transformer encoder** to semantically compare a patient's free-text symptoms against an in-memory vector database of historical cases. It predicts the most appropriate medical specialist based on embedding similarity metrics.

### 2. Clinical Risk Stratifier
Parses and evaluates complex clinical diagnosis notes using rule-based parsing algorithms to automatically assign a risk tier (Low, Medium, High). It highlights critical phrases and flags whether a Second Opinion is medically warranted.

### 3. Drug Interaction Intelligence
Utilizes a pharmacological Knowledge Graph constructed with **NetworkX** to map and traverse medication constraints. Automatically evaluates regimes of drugs to spot dangerous combinations, predicting the interaction severity and explaining the underlying physiological mechanism.

## 🏗️ Technical Architecture
- **Backend API**: Python, FastAPI
- **Reactive UI**: Streamlit 
- **AI/ML & Data Structures**:
  - `sentence-transformers` for intelligent vectorization.
  - Custom in-memory vector store built with `numpy` for swift nearest-neighbor extraction.
  - `networkx` for modeling multivariate interaction pathways.

---

## ⚙️ Local Installation

**Prerequisite:** Python 3.12 (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shreyshrivastava/ai-healthcare-intel-engine.git
   cd ai-healthcare-intel-engine
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python3.12 -m venv .venv312
   source .venv312/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Running the Services

This clinical suite operates with an independent backend API and an interactive frontend client.

### 1. Launch the FastAPI Backend
```bash
source .venv312/bin/activate
uvicorn api.main:app --reload --port 8000
```
*(Interactive API documentation is automatically exposed at `http://localhost:8000/docs`)*

### 2. Launch the Streamlit Client (In a new terminal)
```bash
source .venv312/bin/activate
streamlit run frontend/app.py
```
*(The UI dashboard will be accessible at `http://localhost:8501`)*

---

## 💾 Optional: Data Pipeline Hooks
The application features hooks to convert raw external datasets (like CSVs) into the strict schema JSON formats used by the internal models:

```bash
python -m services.symptom_specialist.prepare_external_symptoms
python -m services.second_opinion.prepare_external_risk
python -m services.drug_interaction.prepare_external_ddi
```

*Note: The raw external datasets located under `data/external/` are explicitly added to `.gitignore`. Templates (`*.example.csv`) are provided for context.*

## 🤝 Contributing
Contributions, issues, and feature requests are welcome. Feel free to open a Pull Request!

## 📝 License
This project is publicly available under the MIT License.
