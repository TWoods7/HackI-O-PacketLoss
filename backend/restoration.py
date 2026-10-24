"""Restoration-time estimate (owner: AN). Shapes: docs/API_CONTRACT.md.

Labor numbers below are copied from data/raw/Install_Labor_HackOHIO.xlsx (install + removal hours).
TODO(AN): replace the placeholder formula in estimate() with bundles, upstream sequencing,
queueing, and ranges calibrated on historical repair durations.
"""

ILM = 4.5  # indirect labor multiplier: drive time, safety briefing, setup

# (install_h, removal_h) per component
POLE = {"small": (1.942, 0.764), "medium": (2.503, 0.927), "large": (3.368, 1.153)}  # 25-35 / 40-55 / 60+ ft
CROSSARM = (0.374, 0.212)
BRACKET = (0.617, 0.254)
ANCHOR = (0.397, 0.119)
EQUIPMENT_LEAD = (0.650, 0.206)
GROUNDING = (0.532, 0.153)
GUYING = (0.367, 0.162)
DEAD_END = (0.108, 0.064)
INSULATOR = (0.049, 0.039)
PIN = (0.066, 0.042)
RECLOSER = (0.573, 0.525)
SECONDARY_ATTACHMENT = (0.233, 0.127)
SERVICE = (1.693, 0.480)
SWITCH = (1.758, 1.010)
FUSE_CUTOUT = (0.256, 0.128)
CONNECTOR_AVG = (0.215, 0.045)
TRANSFORMER_KVA = {10: (1.189, 0.808), 15: (1.184, 0.800), 25: (1.188, 0.806), 37: (1.238, 0.882),
                   50: (1.245, 0.891), 75: (1.278, 0.937), 100: (1.280, 0.944), 167: (1.280, 0.944),
                   250: (1.330, 0.962), 333: (1.355, 0.976), 500: (1.380, 0.987), 833: (1.364, 0.980)}

# Adders (hours, install only)
RESTRICTED_ACCESS = 0.5
BACKYARD = 0.5
REMOTE_SITE = 1.312
SPECIALIZED_HANDLING = 0.5


def _h(c):
    return c[0] + c[1]


# PLACEHOLDER bundles so the UI sliders move from hour 1. AN: refine with structure_drawings.pdf.
BUNDLE_HOURS = {
    "pole": _h(POLE["medium"]) + _h(CROSSARM) + 3 * (_h(INSULATOR) + _h(PIN)) + _h(GUYING) + _h(GROUNDING),
    "wire": 2 * _h(DEAD_END) + 4 * _h(CONNECTOR_AVG),
    "switch": _h(FUSE_CUTOUT),
    "equipment": _h(TRANSFORMER_KVA[25]) + _h(EQUIPMENT_LEAD),
}


def estimate(context_id: str, scenario: dict) -> dict:
    damage = scenario.get("damage") or [{"type": "pole", "qty": 1}]
    crews = max(1, int(scenario.get("crews", 2)))
    storm = int(scenario.get("storm", 2))
    access = bool(scenario.get("access_issue", False))

    direct = sum(BUNDLE_HOURS[d["type"]] * d.get("qty", 1) for d in damage)
    direct += RESTRICTED_ACCESS * len(damage) if access else 0
    labor = direct * ILM
    likely = labor / crews * (1 + 0.25 * storm)  # placeholder storm queue factor
    return {
        "low_h": round(likely * 0.6, 1),
        "likely_h": round(likely, 1),
        "high_h": round(likely * 1.8, 1),
        "labor_hours": round(labor, 1),
        "sequence": ["Repair upstream damage first", "Repair damage on your line", "Re-energize your transformer"],
        "movers": [{"label": "Access blocked", "delta_h": round(RESTRICTED_ACCESS * len(damage) * ILM / crews, 1)},
                   {"label": "Double the crews", "delta_h": round(likely / 2 - likely, 1)}],
        "label": "Model estimate, not confirmed AEP restoration time",
    }
