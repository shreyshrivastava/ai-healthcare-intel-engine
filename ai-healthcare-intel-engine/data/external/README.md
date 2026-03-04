## External DDI data

This folder is intended for **real public drug–drug interaction datasets**.

The serving code does NOT depend on any specific dataset format. Instead, you:

1. Download and preprocess a dataset (e.g. TWOSIDES, DrugBank export, or another
   research DDI corpus) into a simple CSV:

   - Path: `data/external/raw_ddi.csv`
   - Columns (header row):
     - `drug_a` – generic / ingredient name, normalized (RxNorm-style) where possible
     - `drug_b` – generic / ingredient name
     - `risk_level` – free text or coded severity (e.g. major/moderate/minor)
     - `mechanism` – short description of the interaction mechanism

2. Run:

   ```bash
   cd ai-healthcare-intel-engine
   python -m services.drug_interaction.prepare_external_ddi
   ```

   This writes `data/demo/ddi_pairs.json` in the internal schema used by the
   knowledge-graph builder.

3. Restart the FastAPI app; the DDI module will now back its knowledge graph
   with your real dataset instead of the small hard-coded demo list.

### Templates

This repo includes starter templates you can copy:

- `data/external/raw_ddi.example.csv` → copy to `data/external/raw_ddi.csv`

### Drug name normalization (RxNorm-style)

The runtime code supports a simple alias system (see
`services/drug_interaction/inference.py`) and can be extended by creating:

- `data/external/drug_aliases.json`

with contents like:

```json
{
  "acetaminophen": "paracetamol",
  "tylenol": "paracetamol",
  "bactrim": "trimethoprim-sulfamethoxazole"
}
```

These aliases are applied before graph lookup, approximating RxNorm-style
ingredient normalization for portfolio purposes.

