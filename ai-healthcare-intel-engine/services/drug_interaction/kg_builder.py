from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


DEMO_DDI_PAIRS_PATH = Path(__file__).resolve().parents[2] / "data" / "demo" / "ddi_pairs.json"


def build_demo_ddi_kg() -> nx.MultiDiGraph:
    """
    Demonstration knowledge graph backed by a small curated JSON file of
    common interactions.
    """
    g = nx.MultiDiGraph()

    if DEMO_DDI_PAIRS_PATH.exists():
        with DEMO_DDI_PAIRS_PATH.open("r", encoding="utf-8") as f:
            pairs = json.load(f)
    else:
        pairs = []

    for p in pairs:
        a = str(p["drug_a"]).strip().lower()
        b = str(p["drug_b"]).strip().lower()
        risk = str(p.get("risk_level", "Unknown")).strip()
        mechanism = str(p.get("mechanism", "")).strip()

        g.add_node(a, type="drug")
        g.add_node(b, type="drug")
        g.add_edge(
            a,
            b,
            key="ddi",
            relation="interacts_with",
            risk_level=risk,
            mechanism=mechanism,
        )

    return g

