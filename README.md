# ⚡ FastReact

> **FastAPI + React = One Unified Stack**  
> Zero config. One server. Python tracebacks in your browser.

---

## What is FastReact?

FastReact is a Python library that bridges **FastAPI** and **React** into a single seamless stack.

- 🐍 FastAPI thinks it's serving Jinja templates — it's actually serving React
- ⚡ React thinks it's a normal Vite app — it's tunneled through FastAPI
- 🔴 Python errors appear as beautiful overlays in the browser (just like React's own error screen)
- 🚀 One `uvicorn` instance serves everything — in dev AND production

---

## Install

```bash
pip install fastreact
```

---

## Scaffold a React Project

Inside your FastAPI project directory:

```bash
fastreact create frontend
```

This runs `npm create vite@latest` under the hood and wires everything up automatically — proxy config, build output path, the works.

```
your-project/
├── main.py              ← FastAPI entry point
├── frontend/            ← React app (scaffolded by fastreact)
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js   ← pre-configured proxy to FastAPI
│   └── package.json
└── frontend_build/      ← React production build lands here
```

---

## Usage

```python
# main.py
from fastreact import FastReact

app = FastReact(
    react_dir="frontend",       # where your React source lives
    build_dir="frontend_build", # where npm run build outputs
    dev=False,                  # set True in development
    traceback_overlay=True,     # Python errors in browser
)

@app.get("/api/users")
def get_users():
    return {"users": ["Alice", "Bob"]}

@app.get("/api/products")
def get_products():
    return {"products": ["Widget", "Gadget"]}
```

Run it:
```bash
uvicorn main:app --reload
```

---

## Dev Mode

Start both servers:

```bash
# Terminal 1 — FastAPI
uvicorn main:app --reload

# Terminal 2 — React dev server
cd frontend && npm run dev
```

Enable dev mode in your app:
```python
app = FastReact(dev=True)
```

React dev server runs on `:5173`, FastAPI on `:8000`.  
FastReact tunnels API calls between them — **no CORS issues, ever**.

---

## Traceback Overlay

When a Python error occurs, instead of a plain JSON error, FastReact serves a beautiful error overlay in the browser:

```
┌─────────────────────────────────────────────┐
│ 🔴 FastAPI Traceback — TypeError            │
├─────────────────────────────────────────────┤
│ 'NoneType' object has no attribute 'id'     │
├─────────────────────────────────────────────┤
│ File main.py, line 24                       │
│ >> return db.query(User).filter(...)        │
└─────────────────────────────────────────────┘
```

Just like React's own error screen — but for Python! 🐍

---

## Deployment

```bash
# Build React
cd frontend && npm run build
# Builds to ../frontend_build automatically

# Run in production
uvicorn main:app --host 0.0.0.0 --port 8000
```

With Docker + Nginx reverse proxy, your app becomes globally accessible.  
**One server. One port. One command.**

---

## License

MIT