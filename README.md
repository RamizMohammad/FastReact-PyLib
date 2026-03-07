# ⚡ FastReact

> **FastAPI + React = One Unified Stack**  
> Zero config. One server. Python tracebacks in your browser.

📖 **[Full Usage Guide →](USAGE.md)**

---

## What is FastReact?

FastReact is a Python library that bridges **FastAPI** and **React** into a single seamless stack.

- 🐍 FastAPI thinks it's serving Jinja templates — it's actually serving React
- ⚡ React thinks it's a normal Vite app — it's tunneled through FastAPI
- 🔴 Python errors appear as beautiful overlays in the browser (just like React's own error screen)
- 🔒 Python is the gatekeeper — React can only visit routes you register
- 🚀 One `uvicorn` instance serves everything — in dev AND production

---

## Install

```bash
# FastAPI + React
pip install fastreact

# Flask + React
pip install fastreact[flask]
```

---

## Quick Start

```bash
# 1. Scaffold React inside your FastAPI project
fastreact create frontend

# 2. Start both servers together with live request monitor
fastreact dev main:app --reload --call

# 3. Build for production
cd frontend && npm run build
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Usage

```python
# main.py
from fastreact import FastReact

app = FastReact()

# React page routes — /api/ prefix — browser only
# Postman/curl → 405 Not Allowed
@app.get("/api/")
def home(): pass

@app.get("/api/users")
def users_page(): pass

# Normal data routes — everyone can call
@app.get("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}
```

```bash
uvicorn main:app --reload
```

---

## Flask Support

```python
from fastreact import FlaskReact

app = FlaskReact()

@app.route("/api/users")
def users_page(): pass

@app.route("/users")
def get_users():
    return {"users": ["Alice", "Bob"]}

if __name__ == "__main__":
    app.run()
```

---

## Routing Rules

| Route | Browser | Postman/curl |
|-------|---------|--------------|
| `/api/users` (react prefix) | ✅ React renders | ❌ 405 Not Allowed |
| `/users` (normal route) | ✅ JSON | ✅ JSON |
| `/api/unknown` (unregistered) | ❌ 404 | ❌ 404 |

### Custom prefix

```python
app = FastReact(react_prefix="ui")   # /ui/... becomes React routes
```

---

## CLI

```
fastreact create <n>               Scaffold a new React (Vite) app
fastreact dev <file:app> [opts]    Start FastAPI + React dev servers together

  --reload                         Auto-restart on file save
  --port    <number>               Port number          default: 8000
  --host    <address>              Host address         default: 127.0.0.1
  --call                           Live HTTP request monitor
```

---

## Traceback Overlay

Python errors render as a beautiful browser overlay instead of JSON:

```
🔴 FastAPI Traceback — AttributeError
'NoneType' object has no attribute 'id'

File main.py, line 24, in get_user
    return user.id
    ^^^^^^^^^^^^^^
```

---

## Roadmap

- [x] FastAPI + React unified stack
- [x] Flask + React support
- [x] CLI dev mode — one command starts everything
- [x] Live request monitor (`--call`)
- [x] Python traceback overlay in browser
- [x] Route protection — browser-only React routes
- [x] Auto path normalization
- [ ] `--globalname` — instant public URL via SSH tunnel (v0.2.0)

---

## Documentation

| Guide | Description |
|-------|-------------|
| [USAGE.md](USAGE.md) | Full usage guide with all examples |
| [PUBLISH.md](PUBLISH.md) | How to publish to PyPI |

---

## Author

**Mohammad Ramiz**
- 🌐 [mohammadramiz.in](https://www.mohammadramiz.in)
- 💼 [LinkedIn](https://www.linkedin.com/in/mohammad-ramiz)
- 🐙 [GitHub](https://github.com/RamizMohammad)

---

## License

MIT