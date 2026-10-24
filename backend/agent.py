"""Claude chatbot (owner: JF). Shapes: docs/API_CONTRACT.md.

TODO(JF): tool-use loop with the anthropic SDK. Tools wrap risk.get_risk, restoration.estimate,
alerts.check_alerts, plus prep guidance. Every number must come from a tool result.
"""
import json
from collections.abc import Iterator

MOCK_REPLY = (
    "Your area has a **High** chance of losing power in this storm (medium confidence). "
    "Many homes here are fed by overhead lines, and crews repaired equipment nearby in February 2025. "
    "If an outage happens, our model estimates **4 to 13 hours** to restore power. "
    "This is a model estimate, not a confirmed AEP restoration time."
)


def chat(messages: list[dict], context_id: str | None, scenario: dict | None) -> Iterator[str]:
    for word in MOCK_REPLY.split(" "):
        yield word + " "
    trace = [{"tool": "get_outage_risk", "input": {"context_id": context_id}},
             {"tool": "estimate_restoration", "input": {"context_id": context_id}}]
    yield "\n[[TOOL_TRACE]]" + json.dumps(trace)
