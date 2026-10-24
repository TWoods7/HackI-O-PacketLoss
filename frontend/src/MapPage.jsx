// Map page (owner: AL). Hex risk layer + click-to-inspect, wired to the backend.
/* global google */
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { APIProvider, Map, useMap } from '@vis.gl/react-google-maps'
import { GoogleMapsOverlay } from '@deck.gl/google-maps'
import { H3HexagonLayer } from '@deck.gl/geo-layers'
import { getHexes, getRisk, getRestoration } from './api'

const ROANOKE = { lat: 37.27, lng: -79.94 }
// Colorblind-safe-ish sequential bands; always paired with a text label in the UI
const BAND_COLORS = { Low: [69, 117, 180], Elevated: [254, 224, 144], High: [244, 109, 67], Severe: [165, 0, 38] }

// One deck.gl overlay per mount, attached only once Google has picked raster vs vector.
// GoogleMapsOverlay.setMap() on an uninitialized map leaks a listener; under StrictMode's
// double mount that creates two overlays and crashes in _onDrawRaster (null projection).
function useDeckOverlay(map) {
  const [overlay, setOverlay] = useState(null)

  useEffect(() => {
    if (!map) return
    let created, listener
    const attach = () => {
      created = new GoogleMapsOverlay({ interleaved: true })
      created.setMap(map)
      setOverlay(created)
    }
    if (map.getRenderingType() !== google.maps.RenderingType.UNINITIALIZED) attach()
    else listener = map.addListener('renderingtype_changed', () => { listener.remove(); attach() })
    return () => {
      listener?.remove()
      created?.finalize()
      setOverlay(null)
    }
  }, [map])

  return overlay
}

function HexOverlay({ hexes, onSelect }) {
  const overlay = useDeckOverlay(useMap())

  useEffect(() => {
    if (!overlay) return
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
          // Draw each hex as its own polygon; the default fast path reads the map center
          // on init, which can be invalid before Google Maps is ready.
          highPrecision: true,
          pickable: true,
          onClick: ({ object }) => object && onSelect(object),
          updateTriggers: { getFillColor: hexes },
        }),
      ],
    })
  }, [hexes, overlay, onSelect])

  return null
}

export default function MapPage({ storm, setStorm, selected, setSelected }) {
  const [hexes, setHexes] = useState([])
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
        <Map
          mapId={import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || 'DEMO_MAP_ID'}
          defaultCenter={ROANOKE}
          defaultZoom={11}
          gestureHandling="greedy"
          className="map"
        >
          <HexOverlay hexes={hexes} onSelect={setSelected} />
        </Map>
        <aside className="panel">
          <label>
            Storm severity: <strong>{['Calm', 'Moderate', 'Severe', 'Helene-class'][storm]}</strong>
            <input type="range" min="0" max="3" value={storm} onChange={(e) => setStorm(+e.target.value)} />
          </label>
          {!selected && <p>Click a hexagon on the map to see outage risk for that area.</p>}
          {selected && risk && (
            <section>
              <h2>Model estimate: {risk.band} risk</h2>
              <p>Confidence: {risk.confidence}</p>
              <ul>{risk.factors.map((f) => <li key={f.label}>{f.direction === 'up' ? '▲' : '▼'} {f.plain_text}</li>)}</ul>
            </section>
          )}
          {selected && restoration && (
            <section>
              <h2>If power goes out: {restoration.low_h}–{restoration.high_h} hours</h2>
              <label>
                Crews: {crews}
                <input type="range" min="1" max="8" value={crews} onChange={(e) => setCrews(+e.target.value)} />
              </label>
              <p className="label">{restoration.label}</p>
            </section>
          )}
          {selected && <Link className="button" to="/chat">Ask the assistant about this area →</Link>}
        </aside>
      </div>
    </APIProvider>
  )
}
