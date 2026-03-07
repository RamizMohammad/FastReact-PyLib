export default function Card({ title, children }) {
  return (
    <div style={styles.card}>
      {title && <h3 style={styles.title}>{title}</h3>}
      {children}
    </div>
  )
}

const styles = {
  card: {
    background: "#1a1a1a",
    border: "1px solid #333",
    borderRadius: "12px",
    padding: "1.5rem",
    lineHeight: "1.8",
  },
  title: {
    marginBottom: "1rem",
    color: "#e0e0e0",
    borderBottom: "1px solid #2a2a2a",
    paddingBottom: "0.5rem",
  }
}