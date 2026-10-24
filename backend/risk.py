"""Outage risk (owner: TA). Shapes: docs/API_CONTRACT.md.

TODO(TA): load data/processed/ hex features + the trained model and replace the mocks.
"""
from backend.mocks import load

BANDS = [(0.3, "Low"), (0.5, "Elevated"), (0.7, "High"), (1.01, "Severe")]


def band_for(score: float) -> str:
    return next(name for cutoff, name in BANDS if score < cutoff)


def get_hexes(storm: int) -> list[dict]:
    # Mock: real hex footprint + premise/damage counts, placeholder scores scaled by storm level.
    scale = [0.5, 0.8, 1.0, 1.3][storm]
    out = []
    for h in load("hexes"):
        score = round(min(0.99, h["risk_score"] * scale), 2)
        out.append({**h, "risk_score": score, "band": band_for(score)})
    return out


def get_risk(context_id: str, storm: int) -> dict:
    return {**load("risk"), "context_id": context_id, "storm": storm}
