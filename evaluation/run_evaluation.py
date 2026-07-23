from __future__ import annotations

import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

os.environ.setdefault("HEALTHCARE_EMBEDDING_BACKEND", "keyword")

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "ai-healthcare-intel-engine"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from services.drug_interaction.inference import check_interactions  # noqa: E402
from services.second_opinion.model import assess_report_text  # noqa: E402
from services.symptom_specialist.model import display_specialty, get_engine  # noqa: E402

DEMO_DIR = APP_ROOT / "data" / "demo"
RESULTS_JSON = ROOT / "evaluation" / "results.json"
RESULTS_MD = ROOT / "evaluation" / "results.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_symptom_ranking() -> dict:
    cases = load_json(DEMO_DIR / "symptom_specialist_cases.json")
    engine = get_engine()
    rows = []
    top1_hits = 0
    top3_hits = 0
    for case in cases:
        expected = display_specialty(case["specialty"])
        ranked, _ = engine.rank_specialties(case["text"], top_k=3)
        actual = [item.specialty for item in ranked]
        top1_hits += int(bool(actual) and actual[0] == expected)
        top3_hits += int(expected in actual)
        rows.append({"expected": expected, "actual_top3": actual, "top1": bool(actual and actual[0] == expected)})

    return {
        "case_count": len(cases),
        "top1_accuracy": top1_hits / max(1, len(cases)),
        "top3_accuracy": top3_hits / max(1, len(cases)),
        "cases": rows,
    }


def evaluate_second_opinion() -> dict:
    cases = load_json(DEMO_DIR / "second_opinion_cases.json")
    rows = []
    correct = 0
    for case in cases:
        prediction = assess_report_text(case["report_text"])
        is_correct = prediction.risk_level == case["risk_label"]
        correct += int(is_correct)
        rows.append(
            {
                "expected": case["risk_label"],
                "actual": prediction.risk_level,
                "correct": is_correct,
                "contributing_phrases": prediction.contributing_phrases,
            }
        )

    return {"case_count": len(cases), "accuracy": correct / max(1, len(cases)), "cases": rows}


def evaluate_drug_interactions() -> dict:
    pairs = load_json(DEMO_DIR / "ddi_pairs.json")
    positive_correct = 0
    positives = []
    for pair in pairs:
        results = check_interactions([pair["drug_a"], pair["drug_b"]])
        detected = bool(results)
        risk_correct = detected and results[0].risk_level == pair["risk_level"]
        positive_correct += int(risk_correct)
        positives.append(
            {
                "drug_a": pair["drug_a"],
                "drug_b": pair["drug_b"],
                "expected_risk": pair["risk_level"],
                "actual_risk": results[0].risk_level if results else "None",
                "correct": risk_correct,
            }
        )

    negative_cases = [
        ["metformin", "amoxicillin"],
        ["aspirin", "albuterol"],
        ["lisinopril", "omeprazole"],
        ["acetaminophen", "cetirizine"],
    ]
    negative_correct = 0
    negatives = []
    for drugs in negative_cases:
        results = check_interactions(drugs)
        is_correct = not results
        negative_correct += int(is_correct)
        negatives.append({"drugs": drugs, "correct": is_correct})

    return {
        "positive_case_count": len(pairs),
        "negative_case_count": len(negative_cases),
        "positive_recall": positive_correct / max(1, len(pairs)),
        "negative_specificity": negative_correct / max(1, len(negative_cases)),
        "positives": positives,
        "negatives": negatives,
    }


def run_evaluation() -> dict:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "embedding_backend": os.getenv("HEALTHCARE_EMBEDDING_BACKEND", "keyword"),
        },
        "symptom_specialist": evaluate_symptom_ranking(),
        "second_opinion": evaluate_second_opinion(),
        "drug_interactions": evaluate_drug_interactions(),
    }


def write_markdown(results: dict, path: Path) -> None:
    symptom = results["symptom_specialist"]
    second = results["second_opinion"]
    ddi = results["drug_interactions"]
    lines = [
        "# Evaluation Results",
        "",
        "Evaluation uses synthetic/demo cases committed to the repository. These results are regression evidence, not clinical accuracy claims.",
        "",
        f"- Generated at: `{results['generated_at']}`",
        f"- Embedding backend: `{results['environment']['embedding_backend']}`",
        "",
        "## Summary",
        "",
        f"- Symptom specialist top-1 accuracy: `{symptom['top1_accuracy']:.2%}` over `{symptom['case_count']}` cases",
        f"- Symptom specialist top-3 accuracy: `{symptom['top3_accuracy']:.2%}` over `{symptom['case_count']}` cases",
        f"- Second-opinion risk accuracy: `{second['accuracy']:.2%}` over `{second['case_count']}` cases",
        f"- DDI positive recall: `{ddi['positive_recall']:.2%}` over `{ddi['positive_case_count']}` known interactions",
        f"- DDI negative specificity: `{ddi['negative_specificity']:.2%}` over `{ddi['negative_case_count']}` negative pairs",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = run_evaluation()
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results, RESULTS_MD)

    checks = [
        results["symptom_specialist"]["top3_accuracy"] >= 0.80,
        results["second_opinion"]["accuracy"] >= 0.80,
        results["drug_interactions"]["positive_recall"] >= 1.00,
        results["drug_interactions"]["negative_specificity"] >= 1.00,
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
