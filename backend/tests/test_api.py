from fastapi.testclient import TestClient

from backend.app import app
from backend.privacy import scrub

client = TestClient(app)
HEX = "882a8a9731fffff"


def test_hexes_follow_contract():
    rows = client.get("/api/hexes?storm=2").json()
    assert rows and {"h3", "risk_score", "band", "n_premises", "recent_damage"} <= rows[0].keys()


def test_storm_level_raises_risk():
    calm = {r["h3"]: r["risk_score"] for r in client.get("/api/hexes?storm=0").json()}
    severe = {r["h3"]: r["risk_score"] for r in client.get("/api/hexes?storm=3").json()}
    assert severe[HEX] > calm[HEX]


def test_risk_and_location():
    assert client.get(f"/api/location?h3={HEX}").json()["context_id"] == HEX
    assert client.get(f"/api/risk?context_id={HEX}").json()["band"] in {"Low", "Elevated", "High", "Severe"}


def test_restoration_moves_with_crews():
    body = {"context_id": HEX, "scenario": {"damage": [{"type": "pole", "qty": 1}], "crews": 1}}
    one = client.post("/api/restoration", json=body).json()
    body["scenario"]["crews"] = 2
    two = client.post("/api/restoration", json=body).json()
    assert two["likely_h"] < one["likely_h"]
    assert one["low_h"] <= one["likely_h"] <= one["high_h"]


def test_chat_streams_with_trace():
    text = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Will I lose power?"}], "context_id": HEX}).text
    assert "[[TOOL_TRACE]]" in text


def test_privacy_scrub():
    out = scrub("Premise 247057282 at 2347 Gardner Road, device 37800295D00119, life support")
    assert "247057282" not in out and "Gardner" not in out and "37800295D00119" not in out
    assert "life support" not in out.lower()
