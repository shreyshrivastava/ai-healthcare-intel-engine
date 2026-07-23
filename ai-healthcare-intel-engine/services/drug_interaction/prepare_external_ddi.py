"""
Utility script to convert a real public DDI dataset into the simple
`ddi_pairs.json` schema that the demo knowledge graph uses.

Workflow (example with a CSV you prepare yourself):

1. Download a public DDI dataset (e.g. TWOSIDES or similar) and place it under:
   `data/external/raw_ddi.csv`

2. Create/clean a CSV with at least these columns:
      drug_a, drug_b, risk_level, mechanism
   - drug_a / drug_b: normalized generic names (matching RxNorm ingredients where possible)
   - risk_level: one of "Low", "Moderate", "High" (you can map dataset codes)
   - mechanism: short free-text description or empty string

3. Run this script from the project root:

      python -m services.drug_interaction.prepare_external_ddi

   It will read `data/external/raw_ddi.csv` and write
   `data/demo/ddi_pairs.json`, replacing the current demo pairs.

This keeps the serving code decoupled from any particular dataset format.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "external" / "raw_ddi.csv"
OUT_JSON = ROOT / "data" / "demo" / "ddi_pairs.json"


RISK_MAPPING: dict[str, str] = {
    "contraindicated": "High",
    "major": "High",
    "serious": "High",
    "moderate": "Moderate",
    "minor": "Low",
}


def normalize_risk(raw: str) -> str:
    if not raw:
        return "Unknown"
    key = raw.strip().lower()
    return RISK_MAPPING.get(key, "Unknown")


def main() -> None:
    if not RAW_CSV.exists():
        raise SystemExit(
            f"Expected CSV at {RAW_CSV}, please create it with columns: drug_a,drug_b,risk_level,mechanism"
        )

    pairs: list[dict[str, str]] = []
    with RAW_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"drug_a", "drug_b", "risk_level", "mechanism"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            a = (row.get("drug_a") or "").strip().lower()
            b = (row.get("drug_b") or "").strip().lower()
            if not a or not b:
                continue
            risk = normalize_risk(row.get("risk_level") or "")
            mechanism = (row.get("mechanism") or "").strip()
            pairs.append(
                {
                    "drug_a": a,
                    "drug_b": b,
                    "risk_level": risk,
                    "mechanism": mechanism,
                }
            )

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(pairs, f, indent=2)

    print(f"Wrote {len(pairs)} interaction pairs to {OUT_JSON}")


if __name__ == "__main__":
    main()
