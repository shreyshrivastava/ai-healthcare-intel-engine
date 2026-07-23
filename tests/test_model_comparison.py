import json
from pathlib import Path

from evaluation.run_model_comparison import main


def test_model_comparison_runs_keyword_backend(tmp_path, monkeypatch):
    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.delenv("RUN_SENTENCE_TRANSFORMER_COMPARISON", raising=False)

    assert main() == 0

    results = json.loads(Path("evaluation/model_comparison_results.json").read_text())
    keyword = next(row for row in results["backends"] if row["name"] == "keyword")
    optional = next(row for row in results["backends"] if row["name"] == "sentence-transformer")

    assert keyword["status"] == "measured"
    assert keyword["metrics"]["case_count"] >= 20
    assert optional["status"] == "skipped"
