import { BrowserRouter, Route, Routes } from "react-router-dom"
import Navbar from "./components/Navbar"
import About from "./pages/About"
import Dashboard from "./pages/Dashboard"
import Home from "./pages/Home"
import Users from "./pages/Users"

export default function App() {
  return (
    <BrowserRouter>
      <div style={styles.app}>
        <Navbar />
        <main style={styles.main}>
          <Routes>
            {/* React page routes — match /api/ prefix */}
            <Route path="/api/" element={<Home />} />
            <Route path="/api/users" element={<Users />} />
            <Route path="/api/dashboard" element={<Dashboard />} />
            <Route path="/api/about" element={<About />} />

            {/* Root redirect to home */}
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

const styles = {
  app: {
    minHeight: "100vh",
    background: "#0f0f0f",
    color: "#e0e0e0",
    fontFamily: "monospace",
  },
  main: {
    padding: "1rem 0",
  }
}