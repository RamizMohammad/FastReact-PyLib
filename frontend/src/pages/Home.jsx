import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import Card from "../components/Card"

export default function Home() {
  const [status, setStatus] = useState(null)

  // Home page fetches from NORMAL data route — /data/status
  useEffect(() => {
    fetch("/data/status")
      .then(r => r.json())
      .then(setStatus)
  }, [])

  return (
    <div style={styles.container}>
      <div style={styles.hero}>
        <h1 style={styles.title}>⚡ FastReact</h1>
        <p style={styles.subtitle}>FastAPI + React — One Unified Stack</p>
      </div>

      <div style={styles.grid}>
        <Card title="🟢 Server Status">
          {status ? (
            <>
              <p>Status: <strong style={styles.green}>{status.status}</strong></p>
              <p>Framework: <strong>{status.framework}</strong></p>
              <p>Version: <strong>{status.version}</strong></p>
            </>
          ) : <p style={styles.muted}>Loading from /data/status...</p>}
        </Card>

        <Card title="🗺️ Navigate">
          <div style={styles.navLinks}>
            <Link to="/api/users" style={styles.navLink}>👥 Users Page</Link>
            <Link to="/api/dashboard" style={styles.navLink}>📊 Dashboard</Link>
            <Link to="/api/about" style={styles.navLink}>ℹ️ About</Link>
          </div>
        </Card>

        <Card title="🔒 Route Rules">
          <p style={styles.muted}>Pages with <code style={styles.code}>/api/</code> prefix:</p>
          <p>• Browser → React renders ✅</p>
          <p>• Postman → 405 Not Allowed ❌</p>
          <p>• Unknown path → 404 ❌</p>
        </Card>
      </div>
    </div>
  )
}

const styles = {
  container: { padding: "2rem", maxWidth: "960px", margin: "0 auto" },
  hero: { textAlign: "center", marginBottom: "2rem" },
  title: { fontSize: "2.5rem", color: "#e74c3c" },
  subtitle: { color: "#888", fontFamily: "monospace" },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "1.5rem",
  },
  green: { color: "#2ecc71" },
  muted: { color: "#888" },
  code: {
    background: "#2a2a2a",
    padding: "0.1rem 0.4rem",
    borderRadius: "4px",
    color: "#e74c3c",
  },
  navLinks: { display: "flex", flexDirection: "column", gap: "0.5rem" },
  navLink: {
    color: "#e0e0e0",
    textDecoration: "none",
    background: "#2a2a2a",
    padding: "0.5rem 1rem",
    borderRadius: "6px",
    fontFamily: "monospace",
  }
}