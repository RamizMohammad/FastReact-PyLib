# ⚡ FastReact — Usage Guide

## Table of Contents

- [⚡ FastReact — Usage Guide](#-fastreact--usage-guide)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Project Structure](#project-structure)
  - [FastAPI + React](#fastapi--react)
    - [Basic Setup](#basic-setup)
    - [Run it](#run-it)
  - [Flask + React](#flask--react)
    - [Run it](#run-it-1)
  - [Routing Rules](#routing-rules)
    - [How it works](#how-it-works)
    - [React in the frontend matches the same paths](#react-in-the-frontend-matches-the-same-paths)
  - [Custom Prefix](#custom-prefix)
  - [Dev Mode](#dev-mode)
    - [One command — both servers](#one-command--both-servers)
    - [Live request monitor](#live-request-monitor)
  - [CLI Reference](#cli-reference)
    - [`fastreact create <n>`](#fastreact-create-n)
    - [`fastreact dev <file:app> [options]`](#fastreact-dev-fileapp-options)
  - [Traceback Overlay](#traceback-overlay)
  - [Production Deployment](#production-deployment)
    - [Build React](#build-react)
    - [Run with Uvicorn](#run-with-uvicorn)
    - [Docker + Nginx](#docker--nginx)
  - [Configuration Reference](#configuration-reference)
    - [FastReact (FastAPI)](#fastreact-fastapi)
    - [FlaskReact (Flask)](#flaskreact-flask)
  - [Author](#author)

---

## Installation

```bash
# FastAPI + React
pip install fastreact

# Flask + React
pip install fastreact[flask]
```

---

## Project Structure

After running `fastreact create frontend` your project looks like:

```
your-project/
├── main.py                  ← FastAPI/Flask entry point
├── frontend/                ← React source (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── pages/
│   ├── vite.config.js       ← pre-configured proxy to FastAPI
│   └── package.json
├── frontend_build/          ← production build output (git ignored)
├── pyproject.toml
└── README.md
```

---

## FastAPI + React

### Basic Setup

```python
# main.py
from fastreact import FastReact

app = FastReact()

# React page routes — /api/ prefix — browser only
# Postman/curl hitting these gets 405 Not Allowed
@app.get("/api/")
def home(): pass

@app.get("/api/users")
def users_page(): pass

@app.get("/api/dashboard")
def dashboard_page(): pass

# Normal data routes — everyone can call these
@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob", "Charlie"]}

@app.get("/status")
def get_status():
    return {"status": "online"}
```

### Run it

```bash
uvicorn main:app --reload
```

---

## Flask + React

```python
# main.py
from fastreact import FlaskReact

app = FlaskReact()

# React page routes
@app.route("/api/")
def home(): pass

@app.route("/api/users")
def users_page(): pass

# Normal data routes
@app.route("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}

if __name__ == "__main__":
    app.run(debug=True)
```

### Run it

```bash
python main.py
```

---

## Routing Rules

This is the core concept of FastReact — **Python is the gatekeeper**.

| Route type | Prefix | Browser | Postman/curl |
|------------|--------|---------|--------------|
| React page | `/api/users` | ✅ React renders | ❌ 405 Not Allowed |
| Normal route | `/users` | ✅ JSON response | ✅ JSON response |
| Unregistered | `/api/unknown` | ❌ 404 page | ❌ 404 page |

### How it works

```
Browser visits /api/users
        |
        ▼
Is /api/ a registered React page route?
        |
        ├── YES + browser request  → serve index.html → React Router renders
        ├── YES + Postman/curl     → 405 Not Allowed
        └── NO                    → 404 FastReact page
```

### React in the frontend matches the same paths

```jsx
// App.jsx
<Routes>
  <Route path="/api/" element={<Home />} />
  <Route path="/api/users" element={<Users />} />
  <Route path="/api/dashboard" element={<Dashboard />} />
</Routes>
```

---

## Custom Prefix

Don't want `/api/` as your React prefix? Change it:

```python
# Any of these work — FastReact auto-normalizes slashes
app = FastReact(react_prefix="ui")      # /ui/... is React
app = FastReact(react_prefix="pages")   # /pages/... is React
app = FastReact(react_prefix="/app/")   # /app/... is React
```

Then your routes use the new prefix:

```python
app = FastReact(react_prefix="ui")

@app.get("/ui/")
def home(): pass

@app.get("/ui/users")
def users_page(): pass
```

---

## Dev Mode

### One command — both servers

```bash
fastreact dev main:app --reload
```

This starts:
- Uvicorn on `:8000`
- Vite dev server on `:5173`
- Auto-proxies all routes from Vite → FastAPI

Visit `http://localhost:5173` — hot reload works on both sides.

### Live request monitor

```bash
fastreact dev main:app --reload --call
```

Every request shows up colored in real time:

```
18:42:01  GET      /users                      200
18:42:03  POST     /users                      201
18:42:05  GET      /api/unknown                404
18:42:07  DELETE   /users/1                    200
```

---

## CLI Reference

### `fastreact create <n>`

Scaffold a new Vite React app inside your project.

```bash
fastreact create frontend
```

- Runs `npm create vite@latest` under the hood
- Auto-installs npm dependencies
- Injects proxy config into `vite.config.js`

---

### `fastreact dev <file:app> [options]`

Start FastAPI + Vite together.

```bash
fastreact dev main:app --reload
fastreact dev main:app --reload --port 8000
fastreact dev main:app --reload --host 0.0.0.0
fastreact dev main:app --reload --call
```

| Option | Description | Default |
|--------|-------------|---------|
| `--reload` | Auto-restart on save | off |
| `--port` | Port number | 8000 |
| `--host` | Host address | 127.0.0.1 |
| `--workers` | Worker processes | 1 |
| `--call` | Live request monitor | off |

---

## Traceback Overlay

When a Python error occurs FastReact shows it in the browser instead of raw JSON:

```python
# This crash...
@app.get("/api/users")
def users():
    x = None
    return x.id  # ← crashes here
```

Shows in browser as:

```
🔴 FastAPI Traceback — AttributeError
'NoneType' object has no attribute 'id'

File main.py, line 5, in users
    return x.id
    ^^^^^^^^^^^
```

Clean, filtered — no internal framework noise. Only your code.

Disable it:

```python
app = FastReact(traceback_overlay=False)
```

---

## Production Deployment

### Build React

```bash
cd frontend
npm run build
# outputs to ../frontend_build automatically
```

### Run with Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker + Nginx

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install fastreact
RUN apt-get update && apt-get install -y nodejs npm
RUN cd frontend && npm run build
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Nginx reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Configuration Reference

### FastReact (FastAPI)

```python
app = FastReact(
    react_dir="frontend",        # React source folder
    build_dir="frontend_build",  # Production build output folder
    dev=False,                   # Dev mode (proxy to Vite)
    dev_port=5173,               # Vite dev server port
    traceback_overlay=True,      # Show Python errors in browser
    title="My App",              # FastAPI app title
    react_prefix="api",          # Prefix that marks React page routes
)
```

### FlaskReact (Flask)

```python
app = FlaskReact(
    react_dir="frontend",        # React source folder
    build_dir="frontend_build",  # Production build output folder
    traceback_overlay=True,      # Show Python errors in browser
    title="My App",              # Flask app name
    react_prefix="api",          # Prefix that marks React page routes
)
```

---

## Author

**Mohammad Ramiz**
- 🌐 Portfolio → [mohammadramiz.in](https://www.mohammadramiz.in)
- 💼 LinkedIn → [Mohammad Ramiz](https://www.linkedin.com/in/mohammad-ramiz)
- 🐙 GitHub → [RamizMohammad](https://github.com/RamizMohammad)