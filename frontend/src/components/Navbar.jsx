import { Link, useLocation } from "react-router-dom"

const links = [
  { to: "/api/", label: "🏠 Home" },
  { to: "/api/users", label: "👥 Users" },
  { to: "/api/dashboard", label: "📊 Dashboard" },
  { to: "/api/about", label: "ℹ️ About" },
]

export default function Navbar() {
  const location = useLocation()

  return (
    <nav style={styles.nav}>
      <span style={styles.brand}>⚡ FastReact</span>
      <div style={styles.links}>
        {links.map(link => (
          <Link
            key={link.to}
            to={link.to}
            style={{
              ...styles.link,
              ...(location.pathname === link.to ? styles.active : {})
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}

const styles = {
  nav: {
    background: "#111",
    borderBottom: "1px solid #333",
    padding: "1rem 2rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    fontFamily: "monospace",
  },
  brand: {
    fontSize: "1.2rem",
    color: "#e74c3c",
    fontWeight: "bold",
  },
  links: {
    display: "flex",
    gap: "0.5rem",
  },
  link: {
    color: "#aaa",
    textDecoration: "none",
    padding: "0.4rem 0.8rem",
    borderRadius: "6px",
    fontSize: "0.9rem",
    transition: "all 0.2s",
  },
  active: {
    background: "#1a1a1a",
    color: "#e0e0e0",
    border: "1px solid #333",
  }
}