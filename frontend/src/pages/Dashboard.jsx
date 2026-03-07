import { useEffect, useState } from "react"
import Card from "../components/Card"

export default function Dashboard() {
  const [status, setStatus] = useState(null)
  const [count, setCount] = useState(null)
  const [local, setLocal] = useState(0)

  // Both fetches hit NORMAL data routes
  useEffect(() => {
    fetch("/data/status").then(r => r.json()).then(setStatus)
    fetch("/data/count").then(r => r.json()).then(d => setCount(d.count))
  }, [])

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>📊 Dashboard</h2>
      <p style={styles.hint}>
        Data from <code style={styles.code}>/data/status</code> and <code style={styles.code}>/data/count</code>
      </p>

      <div style={styles.grid}>
        <Card title="🟢 Server Status">
          {status ? (
            <>
              <p>Status: <strong style={styles.green}>{status.status}</strong></p>
              <p>Framework: <strong>{status.framework}</strong></p>
              <p>Version: <strong>{status.version}</strong></p>
            </>
          ) : <p style={styles.muted}>Loading...</p>}
        </Card>

        <Card title="🔢 Counter">
          <p>From API: <strong>{count ?? "..."}</strong></p>
          <p>Local clicks: <strong style={styles.red}>{local}</strong></p>
          <button style={styles.button} onClick={() => setLocal(l => l + 1)}>
            + Click Me
          </button>
        </Card>

        <Card title="📡 API Routes">
          <p style={styles.muted}>Normal routes (open to all):</p>
          <p><code style={styles.code}>/data/status</code></p>
          <p><code style={styles.code}>/data/users</code></p>
          <p><code style={styles.code}>/data/count</code></p>
        </Card>

        <Card title="🔒 Page Routes">
          <p style={styles.muted}>React routes (browser only):</p>
          <p><code style={styles.code}>/api/</code></p>
          <p><code style={styles.code}>/api/users</code></p>
          <p><code style={styles.code}>/api/dashboard</code></p>
          <p><code style={styles.code}>/api/about</code></p>
        </Card>
      </div>
    </div>
  )
}

const styles = {
  container: { padding: "2rem", maxWidth: "900px", margin: "0 auto" },
  heading: { color: "#e0e0e0", marginBottom: "0.5rem" },
  hint: { color: "#888", fontFamily: "monospace", marginBottom: "1.5rem", fontSize: "0.85rem" },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: "1.5rem",
  },
  green: { color: "#2ecc71" },
  red: { color: "#e74c3c" },
  muted: { color: "#888", marginBottom: "0.5rem" },
  code: { background: "#2a2a2a", padding: "0.1rem 0.4rem", borderRadius: "4px", color: "#e74c3c", display: "block", margin: "0.2rem 0" },
  button: {
    marginTop: "0.8rem",
    background: "#e74c3c",
    color: "white",
    border: "none",
    padding: "0.5rem 1.2rem",
    borderRadius: "6px",
    cursor: "pointer",
    fontFamily: "monospace",
    fontSize: "0.9rem",
  }
}