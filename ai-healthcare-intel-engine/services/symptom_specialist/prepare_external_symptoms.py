from __future__ import annotations

"""
Convert a real symptom→specialist dataset into the simple
`symptom_specialist_cases.json` schema used by the engine.

Expected input CSV:

  data/external/symptom_specialist_raw.csv

Columns (header row):
  text,specialty

Where:
  - text: free-text symptom/complaint or short note snippet
  - specialty: raw specialty name (any case; will be normalized)
"""

import csv
import json
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "external" / "symptom_specialist_raw.csv"
OUT_JSON = ROOT / "data" / "demo" / "symptom_specialist_cases.json"


SPECIALTY_MAP: Dict[str, str] = {
    "cardio": "Cardiology",
    "cardiology": "Cardiology",
    "cardiologist": "Cardiology",
    "pulmonology": "Pulmonology",
    "pulmonary": "Pulmonology",
    "respiratory": "Pulmonology",
    "endocrine": "Endocrinology",
    "endocrinology": "Endocrinology",
    "neurology": "Neurology",
    "neuro": "Neurology",
    "rheumatology": "Rheumatology",
    "rheum": "Rheumatology",
    "internal medicine": "Internal Medicine",
    "im": "Internal Medicine",
}


def normalize_specialty(raw: str) -> str | None:
    key = (raw or "").strip().lower()
    if not key:
        return None
    return SPECIALTY_MAP.get(key, raw.strip() or None)


def main() -> None:
    if not RAW_CSV.exists():
        raise SystemExit(
            f"Expected CSV at {RAW_CSV}, with columns: text,specialty"
        )

    cases: List[Dict[str, str]] = []
    with RAW_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"text", "specialty"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(
                f"CSV is missing required columns: {', '.join(sorted(missing))}"
            )

        for row in reader:
            text = (row.get("text") or "").strip()
            spec_raw = (row.get("specialty") or "").strip()
            if not text or not spec_raw:
                continue
            specialty = normalize_specialty(spec_raw)
            if not specialty:
                continue
            cases.append({"text": text, "specialty": specialty})

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

    print(f"Wrote {len(cases)} cases to {OUT_JSON}")


if __name__ == "__main__":
    main()

