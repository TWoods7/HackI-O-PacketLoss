// Starter map (owner: AL). Hex risk layer + click-to-inspect, wired to the mock backend.
import { useEffect, useMemo, useState } from 'react'
import { APIProvider, Map, useMap } from '@vis.gl/react-google-maps'
import { GoogleMapsOverlay } from '@deck.gl/google-maps'
import { H3HexagonLayer } from '@deck.gl/geo-layers'
import { getHexes, getRisk, getRestoration } from './api'

const ROANOKE = { lat: 37.27, lng: -79.94 }
// Colorblind-safe-ish sequential bands; always paired with a text label in the UI
const BAND_COLORS = { Low: [69, 117, 180], Elevated: [254, 224, 144], High: [244, 109, 67], Severe: [165, 0, 38] }

function HexOverlay({ hexes, onSelect }) {
  const map = useMap()
  const overlay = useMemo(() => new GoogleMapsOverlay({ interleaved: true }), [])

  useEffect(() => {
    if (!map) return
    overlay.setMap(map)
    return () => overlay.setMap(null)
  }, [map, overlay])

  useEffect(() => {
    overlay.setProps({
      layers: [
        new H3HexagonLayer({
          id: 'risk-hexes',
          data: hexes,
          getHexagon: (d) => d.h3,
          getFillColor: (d) => [...BAND_COLORS[d.band], 140],
          getLineColor: [255, 255, 255, 80],
          lineWidthMinPixels: 0.5,
          extruded: false,
          pickable: true,
          onClick: ({ object }) => object && onSelect(object),
          updateTriggers: { getFillColor: hexes },
        }),
      ],
    })
  }, [hexes, overlay, onSelect])

  return null
}

export default function App() {
  const [storm, setStorm] = useState(2)
  const [hexes, setHexes] = useState([])
  const [selected, setSelected] = useState(null)
  const [risk, setRisk] = useState(null)
  const [crews, setCrews] = useState(2)
  const [restoration, setRestoration] = useState(null)

  useEffect(() => { getHexes(storm).then(setHexes) }, [storm])

  useEffect(() => {
    if (!selected) return
    getRisk(selected.h3, storm).then(setRisk)
    getRestoration(selected.h3, { damage: [{ type: 'pole', qty: 1 }], crews, access_issue: false, storm }).then(setRestoration)
  }, [selected, storm, crews])

  return (
    <APIProvider apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <div className="layout">
        <Map defaultCenter={ROANOKE} defaultZoom={11} gestureHandling="greedy" disableDefaultUI={false} className="map">
          <HexOverlay hexes={hexes} onSelect={setSelected} />
        </Map>
        <aside className="panel">
          <h1>AI Outage Concierge</h1>
          <label>
            Storm severity: <strong>{['Calm', 'Moderate', 'Severe', 'Helene-class'][storm]}</strong>
            <input type="range" min="0" max="3" value={storm} onChange={(e) => setStorm(+e.target.value)} />
          </label>
          {!selected && <p>Click a hexagon on the map to see outage risk for that area.</p>}
          {risk && (
            <section>
              <h2>Model estimate: {risk.band} risk</h2>
              <p>Confidence: {risk.confidence}</p>
              <ul>{risk.factors.map((f) => <li key={f.label}>{f.direction === 'up' ? '▲' : '▼'} {f.plain_text}</li>)}</ul>
            </section>
          )}
          {restoration && (
            <section>
              <h2>If power goes out: {restoration.low_h}–{restoration.high_h} hours</h2>
              <label>
                Crews: {crews}
                <input type="range" min="1" max="8" value={crews} onChange={(e) => setCrews(+e.target.value)} />
              </label>
              <p className="label">{restoration.label}</p>
            </section>
          )}
        </aside>
      </div>
    </APIProvider>
  )
}
