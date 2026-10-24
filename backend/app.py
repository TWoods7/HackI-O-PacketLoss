"""FastAPI entry point. Run from repo root: .venv/bin/uvicorn backend.app:app --reload"""
from pathlib import Path

import h3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from backend import agent, alerts, restoration, risk  # noqa: E402  (after load_dotenv)
from backend.mocks import load  # noqa: E402

app = FastAPI(title="AI Outage Concierge")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

Storm = Query(2, ge=0, le=3)


class Damage(BaseModel):
    type: str = Field(pattern="^(pole|wire|switch|equipment)$")
    qty: int = Field(1, ge=0, le=50)


class Scenario(BaseModel):
    damage: list[Damage] = []
    crews: int = Field(2, ge=1, le=50)
    access_issue: bool = False
    storm: int = Field(2, ge=0, le=3)


class RestorationRequest(BaseModel):
    context_id: str
    scenario: Scenario = Scenario()


class AlertsRequest(BaseModel):
    context_id: str
    declared_needs: list[str] = []
    storm: int = Field(2, ge=0, le=3)


class ChatRequest(BaseModel):
    messages: list[dict]
    context_id: str | None = None
    scenario: Scenario | None = None


@app.get("/", include_in_schema=False)
def root():
    # The app itself is the Vite frontend on :5173; the backend root shows the API docs.
    return RedirectResponse("/docs")


@app.get("/api/hexes")
def hexes(storm: int = Storm):
    return risk.get_hexes(storm)


@app.get("/api/location")
def location(h3_index: str | None = Query(None, alias="h3"), premise: str | None = None):
    if h3_index:
        if not h3.is_valid_cell(h3_index):
            raise HTTPException(400, "invalid h3 cell")
        lat, lng = h3.cell_to_latlng(h3_index)
        return {**load("location"), "context_id": h3_index, "center": {"lat": lat, "lng": lng}}
    if premise:
        # TODO(TA/JF): look up the premise's hex via the anonymized ID map
        return {**load("location"), "context_id": premise, "kind": "premise"}
    raise HTTPException(400, "pass h3 or premise")


@app.get("/api/risk")
def get_risk(context_id: str, storm: int = Storm):
    return risk.get_risk(context_id, storm)


@app.post("/api/restoration")
def post_restoration(req: RestorationRequest):
    return restoration.estimate(req.context_id, req.scenario.model_dump())


@app.post("/api/alerts")
def post_alerts(req: AlertsRequest):
    return alerts.check_alerts(req.context_id, req.declared_needs, req.storm)


@app.post("/api/chat")
def post_chat(req: ChatRequest):
    scenario = req.scenario.model_dump() if req.scenario else None
    return StreamingResponse(agent.chat(req.messages, req.context_id, scenario), media_type="text/plain")
