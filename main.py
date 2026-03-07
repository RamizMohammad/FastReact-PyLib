from fastreact import FastReact

app = FastReact(build_dir="frontend_build")

# ──────────────────────────────────────────────
# REACT PAGE ROUTES — /api/ prefix — browser only
# These register the path as "allowed for React"
# Postman/curl → 405 | Unknown path → 404
# ──────────────────────────────────────────────

@app.get("/api/")
def home_page(): pass

@app.get("/api/users")
def users_page(): pass

@app.get("/api/dashboard")
def dashboard_page(): pass

@app.get("/api/about")
def about_page(): pass


# ──────────────────────────────────────────────
# NORMAL DATA ROUTES — no /api/ prefix
# Pure JSON — accessible by everyone
# Postman, curl, React fetch() all work
# ──────────────────────────────────────────────

@app.get("data/status")
def status():
    return {"status": "online", "framework": "FastAPI", "version": "0.1.0"}

@app.get("/data/users")
def get_users():
    return {"users": ["Alice", "Bob", "Charlie", "Diana"]}

@app.get("/data/count")
def get_count():
    return {"count": 42}

@app.get("/")
def home():
    return {"message": "FastReact is running!"}