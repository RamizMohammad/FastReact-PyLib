import Card from "../components/Card"

export default function About() {
  const rules = [
    { prefix: "/api/...", type: "React Page Route", browser: "✅ React renders", postman: "❌ 405 Not Allowed" },
    { prefix: "/data/...", type: "Normal API Route", browser: "✅ JSON response", postman: "✅ JSON response" },
    { prefix: "/", type: "Root Route", browser: "✅ JSON/HTML", postman: "✅ Works" },
  ]

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>ℹ️ About FastReact</h2>

      <Card title="⚡ What is FastReact?">
        <p>FastReact bridges <strong>FastAPI</strong> and <strong>React</strong> into one unified stack.</p>
        <br />
        <p>🐍 Python handles routing + data</p>
        <p>⚛️ React handles UI + navigation</p>
        <p>🔒 Python is the gatekeeper — React can only visit registered routes</p>
        <p>🔴 Python errors show as browser overlays</p>
        <p>🚀 One Uvicorn server in production</p>
      </Card>

      <br />

      <Card title="🗺️ Routing Rules">
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Prefix</th>
              <th style={styles.th}>Type</th>
              <th style={styles.th}>Browser</th>
              <th style={styles.th}>Postman/curl</th>
            </tr>
          </thead>
          <tbody>
            {rules.map(r => (
              <tr key={r.prefix}>
                <td style={styles.td}><code style={styles.code}>{r.prefix}</code></td>
                <td style={styles.td}>{r.type}</td>
                <td style={styles.td}>{r.browser}</td>
                <td style={styles.td}>{r.postman}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  )
}

const styles = {
  container: { padding: "2rem", maxWidth: "800px", margin: "0 auto" },
  heading: { color: "#e0e0e0", marginBottom: "1.5rem" },
  table: { width: "100%", borderCollapse: "collapse", fontFamily: "monospace", fontSize: "0.85rem" },
  th: { textAlign: "left", padding: "0.5rem", borderBottom: "1px solid #333", color: "#888" },
  td: { padding: "0.6rem 0.5rem", borderBottom: "1px solid #222", color: "#ccc" },
  code: { background: "#2a2a2a", padding: "0.1rem 0.4rem", borderRadius: "4px", color: "#e74c3c" },
}