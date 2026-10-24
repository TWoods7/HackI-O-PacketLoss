// App shell (owner: AL): nav bar + pages. Selected area and storm level are shared across pages.
import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import NavBar from './NavBar'
import MapPage from './MapPage'
import ChatPage from './ChatPage'

export default function App() {
  const [storm, setStorm] = useState(2)
  const [selected, setSelected] = useState(null) // hex row from /api/hexes

  return (
    <div className="app">
      <NavBar />
      <main className="page">
        <Routes>
          <Route path="/" element={<MapPage storm={storm} setStorm={setStorm} selected={selected} setSelected={setSelected} />} />
          <Route path="/chat" element={<ChatPage storm={storm} selected={selected} />} />
        </Routes>
      </main>
    </div>
  )
}
