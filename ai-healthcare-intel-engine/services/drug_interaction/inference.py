from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Tuple

import json
from pathlib import Path

import networkx as nx

from api.schemas import DrugInteractionPair
from .kg_builder import build_demo_ddi_kg


_KG: nx.MultiDiGraph | None = None


def get_kg() -> nx.MultiDiGraph:
    global _KG
    if _KG is None:
        _KG = build_demo_ddi_kg()
    return _KG


@dataclass
class InteractionResult:
    drug_a: str
    drug_b: str
    risk_level: str
    explanation: str


import logging

logger = logging.getLogger(__name__)


def mock_rxnorm_api_lookup(drug_name: str) -> str:
    """
    Simulates an Enterprise API call to the NIH RxNorm terminology server 
    to fetch the standardized generic name/RxCUI.
    """
    # A tiny simulated ontology for demonstration
    ontology = {
        "acetaminophen": "paracetamol",
        "tylenol": "paracetamol",
        "tmp-smx": "trimethoprim-sulfamethoxazole",
        "co-trimoxazole": "trimethoprim-sulfamethoxazole",
        "bactrim": "trimethoprim-sulfamethoxazole",
        "hctz": "hydrochlorothiazide",
        "oacs": "oral contraceptives",
        "birth control": "oral contraceptives",
        "nitrates": "nitroglycerin",
    }
    
    # Check external aliases as well for flexibility
    root = Path(__file__).resolve().parents[2]
    alias_path = root / "data" / "external" / "drug_aliases.json"
    if alias_path.exists():
        try:
            with alias_path.open("r", encoding="utf-8") as f:
                user_aliases = json.load(f)
            for k, v in user_aliases.items():
                ontology.setdefault(k.strip().lower(), v.strip().lower())
        except Exception:
            pass

    key = drug_name.strip().lower()
    # Mocks an external HTTP call to https://rxnav.nlm.nih.gov/
    result = ontology.get(key, key)
    if result != key:
        logger.info(f"[RxNorm Engine] Resolved brand name '{key}' -> Standardized Concept '{result}'")
    return result


def canonicalize_drug_name(name: str) -> str:
    """
    Standarize names via medical terminology APIs.
    """
    return mock_rxnorm_api_lookup(name)

RISK_ORDER: Dict[str, int] = {"None": 0, "Low": 1, "Moderate": 2, "High": 3, "Unknown": 0}


def overall_risk_from_pairs(pairs: List[InteractionResult]) -> str:
    if not pairs:
        return "None"
    best = max(pairs, key=lambda p: RISK_ORDER.get(p.risk_level, 0))
    return best.risk_level if best.risk_level else "Unknown"


def check_interactions(drugs: List[str]) -> List[InteractionResult]:
    g = get_kg()
    results: List[InteractionResult] = []
    norm: Dict[str, str] = {}
    for d in drugs:
        canon = canonicalize_drug_name(d)
        # keep the first original formatting we saw
        norm.setdefault(canon, d)

    for a, b in combinations(norm.keys(), 2):
        if g.has_edge(a, b, key="ddi") or g.has_edge(b, a, key="ddi"):
            if g.has_edge(a, b, key="ddi"):
                data = g.get_edge_data(a, b, key="ddi")
            else:
                data = g.get_edge_data(b, a, key="ddi")

            risk = data.get("risk_level", "Unknown")
            mechanism = data.get("mechanism", "Mechanism not specified in demo graph.")
            explanation = f"Knowledge-graph edge indicates {risk} interaction due to {mechanism or 'an unspecified mechanism'}."
            results.append(
                InteractionResult(
                    drug_a=norm[a],
                    drug_b=norm[b],
                    risk_level=risk,
                    explanation=explanation,
                )
            )

    return results


def to_schema_pairs(results: List[InteractionResult]) -> List[DrugInteractionPair]:
    return [
        DrugInteractionPair(
            drug_a=r.drug_a,
            drug_b=r.drug_b,
            risk_level=r.risk_level,
            explanation=r.explanation,
        )
        for r in results
    ]

