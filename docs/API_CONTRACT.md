# API contract

Everyone codes against these shapes. **Change this file (and the shared doc) before changing the code.**
Canonical example responses live in [`backend/mocks/`](../backend/mocks/). The backend serves them until the real modules are wired in.

Base URL in dev: `http://localhost:8000`. The Vite dev server proxies `/api` there.

## Privacy rules (apply to every response)

- The location unit is an **H3 hexagon, resolution 8** (~0.7 km²), or an anonymized premise ID `P-XXXXXX` (salted hash of `premise_nu`).
- `context_id` = an H3 index string **or** a `P-` ID.
- Never return: street addresses, raw `premise_nu`, exact premise coordinates, device/location numbers (`location_n`, `aep_xfmr_l`, …), or life-support flags.
- Circuits are shown only as an alias (`Circuit A12`), never the AEP ID.

## Endpoints

### `GET /api/hexes?storm=<0-3>`
Map layer. `storm`: 0 calm, 1 moderate, 2 severe, 3 Helene-class.
```json
[{"h3": "882a9a1a6bfffff", "risk_score": 0.62, "band": "High", "n_premises": 418, "recent_damage": 7}]
```

### `GET /api/location?h3=<h3>` or `?premise=P-XXXXXX`
```json
{"context_id": "882a9a1a6bfffff", "kind": "hex", "circuit_alias": "Circuit A12",
 "n_premises": 418, "service_type_mix": {"overhead": 0.71, "underground": 0.29},
 "upstream_device_count": 4, "center": {"lat": 37.27, "lng": -79.94}}
```
`center` is the hex center (not a premise location).

### `GET /api/risk?context_id=<id>&storm=<0-3>`
```json
{"context_id": "…", "band": "High", "score": 0.62, "confidence": "Med",
 "factors": [{"label": "Overhead service", "direction": "up", "weight": 0.31,
              "plain_text": "Most homes here are fed by overhead lines, which storms damage more often."}],
 "fallback": false, "storm": 2}
```
- `band`: `Low` | `Elevated` | `High` | `Severe`
- `confidence`: `Low` | `Med` | `High`
- `fallback: true` → "we can't give a reliable estimate here"; UI shows the circuit average and says so.

### `POST /api/restoration`
Request:
```json
{"context_id": "…", "scenario": {"damage": [{"type": "pole", "qty": 1}], "crews": 2, "access_issue": false, "storm": 2}}
```
`damage[].type`: `pole` | `wire` | `switch` | `equipment`

Response:
```json
{"low_h": 4, "likely_h": 7, "high_h": 13, "labor_hours": 31.5,
 "sequence": ["Repair recloser upstream (restores 412 customers)", "Replace pole on your line", "Re-energize transformer"],
 "movers": [{"label": "Access blocked", "delta_h": 6}, {"label": "Double the crews", "delta_h": -3}],
 "label": "Model estimate, not confirmed AEP restoration time"}
```

### `POST /api/alerts`
Request: `{"context_id": "…", "declared_needs": ["medical"], "storm": 2}`
`declared_needs[]`: `medical` | `accessibility` | `critical_facility` (only what the user declares; never inferred).

Response:
```json
{"eligible": true, "reason": "Your area is High risk for this storm.",
 "channels": ["sms", "push", "voice"], "timing": "24 hours before expected landfall",
 "escalation_triggers": ["Estimate exceeds 4 hours → phone call + human follow-up"],
 "messages": {"pre_storm": "…", "outage_confirmed": "…", "estimate_updated": "…", "restored": "…"}}
```

### `POST /api/chat`
Request: `{"messages": [{"role": "user", "content": "Will I lose power?"}], "context_id": "…", "scenario": {…}}`
Response: `text/plain` stream of the assistant's reply. The final line is `\n[[TOOL_TRACE]]` followed by a JSON array of the tool calls used (shown in the UI as "how I got this").
