"""Alert eligibility + proactive messages (owner: JF). Shapes: docs/API_CONTRACT.md.

TODO(JF): implement the rules from docs/PLAN.md and generate messages with Claude (template fallback).
"""
from backend.mocks import load


def check_alerts(context_id: str, declared_needs: list[str], storm: int) -> dict:
    return load("alerts")
