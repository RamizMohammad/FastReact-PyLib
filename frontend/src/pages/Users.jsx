import { useEffect, useState } from "react"
import Card from "../components/Card"

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  // Fetches from NORMAL data route — /data/users
  useEffect(() => {
    fetch("/data/users")
      .then(r => r.json())
      .then(data => {
        setUsers(data.users)
        setLoading(false)
      })
  }, [])

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>👥 Users</h2>
      <p style={styles.hint}>
        Data from <code style={styles.code}>/data/users</code> — normal route, open to all
      </p>

      <Card title="User List">
        {loading ? (
          <p style={styles.muted}>Loading...</p>
        ) : (
          <ul style={styles.list}>
            {users.map((u, i) => (
              <li key={u} style={styles.item}>
                <span style={styles.index}>{i + 1}</span>
                <span>{u}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div style={styles.info}>
        <p>🔒 This page <code style={styles.code}>/api/users</code> is a React route.</p>
        <p>Visiting it from Postman returns <strong style={styles.red}>405 Not Allowed</strong>.</p>
      </div>
    </div>
  )
}

const styles = {
  container: { padding: "2rem", maxWidth: "600px", margin: "0 auto" },
  heading: { color: "#e0e0e0", marginBottom: "0.5rem" },
  hint: { color: "#888", fontFamily: "monospace", marginBottom: "1.5rem", fontSize: "0.85rem" },
  muted: { color: "#888" },
  list: { listStyle: "none", padding: 0 },
  item: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    padding: "0.6rem 0",
    borderBottom: "1px solid #2a2a2a",
  },
  index: {
    background: "#2a2a2a",
    color: "#888",
    width: "1.5rem",
    height: "1.5rem",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "0.75rem",
  },
  code: { background: "#2a2a2a", padding: "0.1rem 0.4rem", borderRadius: "4px", color: "#e74c3c" },
  info: {
    marginTop: "1.5rem",
    background: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: "8px",
    padding: "1rem",
    lineHeight: "1.8",
    fontFamily: "monospace",
    fontSize: "0.85rem",
    color: "#aaa",
  },
  red: { color: "#e74c3c" },
}