# Assumptions and limitations

This list is shown in the app's "How this works" panel and loaded into the chatbot's system prompt. Add a line whenever you make a modeling choice.

## Data
- The data covers ~117k premises on 110 circuits in the Roanoke, VA area (Appalachian Power).
- Storms are derived by clustering damage report dates; the source `Event` field is always "Default".
- Damage repair dates are day-level, so historical durations are known in days, not hours.
- 76 damage records were never repaired (placeholder date 2025-10-24) and are excluded from duration statistics.
- There is no weather data. Storm intensity (0–3) is a scenario input, not a forecast.

## Risk
- Risk is estimated per H3 hexagon (~0.7 km²) from infrastructure (overhead vs underground, pole age, line exposure, upstream devices) and past storm damage.
- The storm level scales the base risk using the damage-rate ratio between small and large past storms.
- When a hexagon has too little data, we show a fallback instead of a number.

## Restoration
- Labor hours per component come from the AEP STORMS labor reference; all direct labor is multiplied by 4.5 for travel, safety briefings, and setup.
- A premise is restored only when all damage on its upstream path is repaired. Upstream damage is fixed first.
- Ranges are calibrated against the Feb 2025 storm and Hurricane Helene (Sep 2024).
- All restoration times are model estimates, not confirmed AEP restoration times.

## Privacy and safety
- No addresses, premise numbers, device IDs, or life-support flags leave the backend.
- Medical or accessibility needs are used only when the customer declares them.
- Safety messages (downed lines, generator use) are fixed text and always shown.
