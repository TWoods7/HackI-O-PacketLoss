import { NavLink } from 'react-router-dom'

export default function NavBar() {
  return (
    <nav className="navbar" aria-label="Main">
      <span className="brand">AI Outage Concierge</span>
      <div className="nav-links">
        <NavLink to="/" end>Map</NavLink>
        <NavLink to="/chat">Chat</NavLink>
      </div>
    </nav>
  )
}
