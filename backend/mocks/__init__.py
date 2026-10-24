import json
from functools import cache
from pathlib import Path

_DIR = Path(__file__).parent


@cache
def load(name: str):
    """Load backend/mocks/<name>.json (the canonical contract examples)."""
    return json.loads((_DIR / f"{name}.json").read_text())
