from __future__ import annotations

import json
import os
import platform
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

os.environ.setdefault("HEALTHCARE_EMBEDDING_BACKEND", "keyword")

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "ai-healthcare-intel-engine"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from api.main import create_app  # noqa: E402
from services.drug_interaction.inference import check_interactions  # noqa: E402
from services.second_opinion.model import assess_report_text  # noqa: E402
from services.symptom_specialist.model import get_engine  # noqa: E402

RESULTS_JSON = ROOT / "benchmarks" / "results.json"
RESULTS_MD = ROOT / "benchmarks" / "results.md"

SYMPTOM_TEXT = "chest pain on exertion with shortness of breath and high blood pressure"
REPORT_TEXT = "Patient admitted to ICU with septic shock requiring ventilator support."
DRUGS = ["warfarin", "aspirin", "metformin"]


def timed(fn):
    start = time.perf_counter()
    value = fn()
    return value, (time.perf_counter() - start) * 1000


def summarize(samples: list[float]) -> dict:
    return {
        "runs": len(samples),
        "min_ms": min(samples),
        "median_ms": statistics.median(samples),
        "max_ms": max(samples),
        "mean_ms": statistics.mean(samples),
    }


def run_benchmarks(iterations: int) -> dict:
    engine = get_engine()
    create_app()
    symptom_ms = []
    second_ms = []
    ddi_ms = []
    startup_ms = []

    for _ in range(iterations):
        _, start_ms = timed(create_app)
        _, symptom_time = timed(lambda: engine.rank_specialties(SYMPTOM_TEXT, top_k=3))
        _, second_time = timed(lambda: assess_report_text(REPORT_TEXT))
        _, ddi_time = timed(lambda: check_interactions(DRUGS))

        startup_ms.append(start_ms)
        symptom_ms.append(symptom_time)
        second_ms.append(second_time)
        ddi_ms.append(ddi_time)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "embedding_backend": os.getenv("HEALTHCARE_EMBEDDING_BACKEND", "keyword"),
        },
        "methodology": {
            "iterations": iterations,
            "data": "Synthetic symptoms, report text, and medication list.",
            "model_downloads": "None in default keyword backend mode.",
        },
        "api_app_creation": summarize(startup_ms),
        "symptom_ranking": summarize(symptom_ms),
        "second_opinion": summarize(second_ms),
        "drug_interactions": summarize(ddi_ms),
    }


def write_markdown(results: dict, path: Path) -> None:
    lines = [
        "# Benchmark Results",
        "",
        "These are one-machine synthetic benchmarks for regression tracking, not production clinical performance claims.",
        "",
        f"- Generated at: `{results['generated_at']}`",
        f"- Python: `{results['environment']['python']}`",
        f"- Platform: `{results['environment']['platform']}`",
        f"- Embedding backend: `{results['environment']['embedding_backend']}`",
        f"- Iterations: `{results['methodology']['iterations']}`",
        "",
        "## Latency",
        "",
    ]
    for label, key in [
        ("API app creation", "api_app_creation"),
        ("Symptom ranking", "symptom_ranking"),
        ("Second-opinion risk", "second_opinion"),
        ("Drug interaction check", "drug_interactions"),
    ]:
        stats = results[key]
        lines.extend(
            [
                f"### {label}",
                "",
                f"- Median latency: `{stats['median_ms']:.2f} ms`",
                f"- Mean latency: `{stats['mean_ms']:.2f} ms`",
                f"- Min/Max latency: `{stats['min_ms']:.2f} ms` / "
                f"`{stats['max_ms']:.2f} ms`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    iterations = max(1, iterations)
    results = run_benchmarks(iterations)
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results, RESULTS_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
