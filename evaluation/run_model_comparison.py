from __future__ import annotations

import importlib
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "ai-healthcare-intel-engine"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

RESULTS_JSON = ROOT / "evaluation" / "model_comparison_results.json"
RESULTS_MD = ROOT / "evaluation" / "model_comparison_results.md"


def reset_symptom_engine(backend: str) -> None:
    os.environ["HEALTHCARE_EMBEDDING_BACKEND"] = backend
    core_models = importlib.import_module("core.models")
    symptom_model = importlib.import_module("services.symptom_specialist.model")
    core_models.get_symptom_encoder.cache_clear()
    symptom_model._engine = None


def evaluate_backend(backend: str) -> dict:
    reset_symptom_engine(backend)
    evaluation = importlib.import_module("evaluation.run_evaluation")
    return evaluation.evaluate_symptom_ranking()


def run_comparison() -> dict:
    backends = [{"name": "keyword", "status": "measured", "metrics": evaluate_backend("keyword")}]

    if os.getenv("RUN_SENTENCE_TRANSFORMER_COMPARISON") == "1":
        try:
            backends.append(
                {
                    "name": "sentence-transformer",
                    "status": "measured",
                    "metrics": evaluate_backend("sentence-transformer"),
                }
            )
        except Exception as exc:
            backends.append(
                {
                    "name": "sentence-transformer",
                    "status": "failed",
                    "reason": str(exc),
                }
            )
    else:
        backends.append(
            {
                "name": "sentence-transformer",
                "status": "skipped",
                "reason": "Set RUN_SENTENCE_TRANSFORMER_COMPARISON=1 after installing requirements-ml.txt.",
            }
        )

    reset_symptom_engine("keyword")
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "backends": backends,
    }


def write_markdown(results: dict, path: Path) -> None:
    lines = [
        "# Model Comparison Results",
        "",
        "Compares symptom-specialist ranking backends on the synthetic evaluation set.",
        "",
        f"- Generated at: `{results['generated_at']}`",
        "",
        "## Backends",
        "",
    ]
    for backend in results["backends"]:
        lines.append(f"### {backend['name']}")
        lines.append("")
        lines.append(f"- Status: `{backend['status']}`")
        if backend["status"] == "measured":
            metrics = backend["metrics"]
            lines.append(f"- Cases: `{metrics['case_count']}`")
            lines.append(f"- Top-1 accuracy: `{metrics['top1_accuracy']:.2%}`")
            lines.append(f"- Top-3 accuracy: `{metrics['top3_accuracy']:.2%}`")
        else:
            lines.append(f"- Reason: {backend.get('reason', 'Not available')}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    results = run_comparison()
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results, RESULTS_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
