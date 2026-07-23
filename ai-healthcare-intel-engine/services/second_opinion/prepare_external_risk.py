"""
Convert a real second-opinion / complexity dataset into a simple
`second_opinion_cases.json` schema suitable for training.

Expected input CSV:

  data/external/second_opinion_raw.csv

Columns (header row):
  report_text,risk_label

Where:
  - report_text: diagnosis summary or report text
  - risk_label: free text or code indicating complexity (e.g. low/medium/high)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_CSV = ROOT / "data" / "external" / "second_opinion_raw.csv"
OUT_JSON = ROOT / "data" / "demo" / "second_opinion_cases.json"


LABEL_MAP: dict[str, str] = {
    "low": "Low",
    "minor": "Low",
    "medium": "Medium",
    "moderate": "Medium",
    "intermediate": "Medium",
    "high": "High",
    "complex": "High",
    "severe": "High",
}


def normalize_label(raw: str) -> str | None:
    key = (raw or "").strip().lower()
    if not key:
        return None
    return LABEL_MAP.get(key, None)


def main() -> None:
    if not RAW_CSV.exists():
        raise SystemExit(f"Expected CSV at {RAW_CSV}, with columns: report_text,risk_label")

    cases: list[dict[str, str]] = []
    with RAW_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"report_text", "risk_label"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            text = (row.get("report_text") or "").strip()
            label_raw = (row.get("risk_label") or "").strip()
            if not text or not label_raw:
                continue
            label = normalize_label(label_raw)
            if not label:
                continue
            cases.append({"report_text": text, "risk_label": label})

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

    print(f"Wrote {len(cases)} cases to {OUT_JSON}")


if __name__ == "__main__":
    main()
