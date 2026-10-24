# HackI-O-PacketLoss: AI Outage Concierge

HackOHI/O 2026, AEP challenge. A Google-Maps-style outage risk map plus a chatbot that answers: *Will I lose power? How long? How do I prepare? Do I qualify for alerts?*

**Source of truth:** [shared plan doc](https://claude.ai/artifact/96uhz9zTUtTxnzUMVKYAN1) · [docs/PLAN.md](docs/PLAN.md) · [docs/API_CONTRACT.md](docs/API_CONTRACT.md) · [docs/assumptions.md](docs/assumptions.md)
Change the contract or an assumption in the docs **before** coding against it.

| Who | Owns | Files |
| --- | --- | --- |
| TA | Data reading + risk model | `pipeline/`, `backend/risk.py` |
| AN | Restoration-time calculator | `backend/restoration.py` |
| AL | Map + UI | `frontend/` |
| JF | Chatbot + backend | `backend/app.py`, `agent.py`, `alerts.py`, `privacy.py` |

Every endpoint already works with mock data (`backend/mocks/`), so you can build against it right away. Replace your module's mock with the real thing when it's ready.

## Setup (once)

```bash
git clone https://github.com/TWoods7/HackI-O-PacketLoss.git && cd HackI-O-PacketLoss
cp .env.example .env                      # add ANTHROPIC_API_KEY

# Python (if `python3 -m venv` complains about ensurepip, run: sudo apt install python3.12-venv)
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt -r pipeline/requirements.txt

# Data (~33 MB, gitignored; contains addresses, so never commit it)
bash scripts/get_data.sh

# Frontend
cd frontend && npm install
echo "VITE_GOOGLE_MAPS_API_KEY=your-key" > .env.local
```

On Windows, use `.venv\Scripts\` instead of `.venv/bin/`, and run `get_data.sh` from Git Bash.

## Run

```bash
.venv/bin/uvicorn backend.app:app --reload     # API on :8000
cd frontend && npm run dev                     # app on :5173 (proxies /api to :8000)
.venv/bin/python -m pipeline.build             # rebuild data/processed/
.venv/bin/python -m pytest backend             # tests
```

## Layout

```
pipeline/   build.py: load shapefiles, circuit-ID map, upstream topology, storm events  (TA)
backend/    FastAPI app + one module per owner; mocks/ = contract examples
frontend/   Vite + React + Google Maps + deck.gl H3 hex layer                          (AL)
scripts/    get_data.sh
docs/       plan, API contract, assumptions
```

## Privacy rules

No street addresses, raw premise numbers, device IDs, or life-support flags ever leave the backend or go to the LLM. Locations are H3 hexagons (resolution 8) or anonymized `P-XXXXXX` IDs.
