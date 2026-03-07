import traceback
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import httpx

from .utils import build_traceback_html, NOT_FOUND_PAGE, NOT_ALLOWED_PAGE, is_browser_request


class FastReact:
    """
    FastReact — FastAPI + React unified stack.

    Route rules:
      - Routes WITH react_prefix (default /api/) → React page routes
          • Browser request  → serves index.html → React Router renders
          • Non-browser      → 405 Not Allowed
          • Unregistered     → 404
      - Routes WITHOUT react_prefix → normal FastAPI routes
          • Work exactly like regular FastAPI (JSON, Jinja, anything)
          • Accessible by everyone (Postman, curl, browser)

    Usage:
        app = FastReact()

        # React page route — browser only
        @app.get("/api/users")
        def users_page(): pass

        # Normal API route — everyone
        @app.get("/data/users")
        def get_users():
            return {"users": [...]}

    Custom prefix:
        app = FastReact(react_prefix="/ui/")
    """

    def __init__(
        self,
        react_dir: str = "frontend",
        build_dir: str = "frontend_build",
        dev: bool = False,
        dev_port: int = 5173,
        traceback_overlay: bool = True,
        title: str = "FastReact App",
        react_prefix: str = "/api/",
    ):
        self.react_dir = Path(react_dir)
        self.build_dir = Path(build_dir)
        self.dev = dev
        self.dev_port = dev_port
        self.traceback_overlay = traceback_overlay
        # auto normalize: "ui/" → "/ui/" , "/ui" → "/ui/" , "ui" → "/ui/"
        react_prefix = react_prefix.strip("/")
        self.react_prefix = "/" + react_prefix + "/"
        self._routes_finalized = False
        self._react_page_routes: set[str] = set()  # registered React page paths

        self._app = FastAPI(title=title)
        self._setup_static()

        if traceback_overlay:
            self._setup_traceback_middleware()

    def _setup_static(self):
        """Mount /assets early."""
        build_dir = self.build_dir
        if not self.dev and build_dir.exists():
            assets_dir = build_dir / "assets"
            if assets_dir.exists():
                self._app.mount(
                    "/assets",
                    StaticFiles(directory=str(assets_dir)),
                    name="assets"
                )

    def _is_react_route(self, path: str) -> bool:
        """Check if path starts with react_prefix."""
        return path.startswith(self.react_prefix) or path == self.react_prefix.rstrip("/")

    def _finalize_routes(self):
        """
        Register catch-all LAST so user API routes are matched first.
        Called on first request via __call__.
        """
        if self._routes_finalized:
            return
        self._routes_finalized = True

        app = self._app
        build_dir = self.build_dir
        dev = self.dev
        dev_port = self.dev_port
        react_page_routes = self._react_page_routes
        react_prefix = self.react_prefix

        # ── Serve root / ─────────────────────────────────────────────
        if not dev and build_dir.exists():

            @app.get("/", response_class=HTMLResponse)
            async def serve_root():
                return FileResponse(str(build_dir / "index.html"))

            # ── Catch-all ─────────────────────────────────────────────
            @app.get("/{full_path:path}", response_class=HTMLResponse)
            async def catch_all(request: Request, full_path: str):
                path = "/" + full_path

                # ── React prefix route (/api/...) ─────────────────────
                if path.startswith(react_prefix) or path == react_prefix.rstrip("/"):

                    # Not registered → 404
                    if path not in react_page_routes:
                        return HTMLResponse(
                            NOT_FOUND_PAGE.format(path=path),
                            status_code=404
                        )

                    # Registered — check if browser
                    accept = request.headers.get("accept", "")
                    if not is_browser_request(accept):
                        # Non-browser (Postman/curl) → 405
                        return HTMLResponse(
                            NOT_ALLOWED_PAGE.format(path=path),
                            status_code=405
                        )

                    # Browser + registered → serve React
                    return FileResponse(str(build_dir / "index.html"))

                # ── Normal route (no prefix) ──────────────────────────
                # Serve index.html for React Router sub-paths
                index = build_dir / "index.html"
                if index.exists():
                    return FileResponse(str(index))

                return HTMLResponse(
                    NOT_FOUND_PAGE.format(path=path),
                    status_code=404
                )

        elif dev:

            @app.get("/", response_class=HTMLResponse)
            async def proxy_root():
                return await _proxy_to_vite("/", dev_port)

            @app.get("/{full_path:path}")
            async def proxy_dev(request: Request, full_path: str):
                path = "/" + full_path

                if path.startswith(react_prefix):
                    if path not in react_page_routes:
                        return HTMLResponse(NOT_FOUND_PAGE.format(path=path), status_code=404)
                    accept = request.headers.get("accept", "")
                    if not is_browser_request(accept):
                        return HTMLResponse(NOT_ALLOWED_PAGE.format(path=path), status_code=405)

                return await _proxy_to_vite(path, dev_port)

        else:
            @app.get("/", response_class=HTMLResponse)
            async def no_react():
                return HTMLResponse("""
                    <html><body style='font-family:monospace;padding:2rem;background:#111;color:#eee'>
                    <h2>⚡ FastReact Running</h2>
                    <p>No React build found.</p>
                    <p>Run: <code>cd frontend && npm run build</code></p>
                    </body></html>
                """)

    def _setup_traceback_middleware(self):
        app = self._app

        @app.middleware("http")
        async def traceback_middleware(request: Request, call_next):
            try:
                response = await call_next(request)
                return response
            except Exception as exc:
                html = build_traceback_html(
                    error_type=type(exc).__name__,
                    error_message=str(exc),
                    traceback_text=traceback.format_exc(),
                    path=request.url.path,
                    framework="FastAPI",
                )
                return HTMLResponse(content=html, status_code=500)

    # ── Decorator delegation ──────────────────────────────────────────────

    def _register(self, method: str, path: str, **kwargs):
        """
        Core registration logic.
        Auto-normalizes path — adds leading slash if missing.
        If path starts with react_prefix → track as React page route.
        The actual response is handled by the catch-all.
        """
        # Auto-normalize: "data/status" → "/data/status"
        if not path.startswith("/"):
            path = "/" + path

        if self._is_react_route(path):
            # Track this path as an allowed React page route
            self._react_page_routes.add(path)
            # Return a pass-through decorator — catch-all handles the response
            def decorator(f):
                return f
            return decorator
        else:
            # Normal FastAPI route — delegate directly
            return getattr(self._app, method)(path, **kwargs)

    def get(self, path: str, **kwargs):
        return self._register("get", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._register("post", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._register("put", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._register("delete", path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self._register("patch", path, **kwargs)

    def include_router(self, router, **kwargs):
        return self._app.include_router(router, **kwargs)

    # ── ASGI entrypoint ───────────────────────────────────────────────────

    async def __call__(self, scope, receive, send):
        self._finalize_routes()
        await self._app(scope, receive, send)


async def _proxy_to_vite(path: str, port: int) -> HTMLResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:{port}{path}")
            return HTMLResponse(content=response.text, status_code=response.status_code)
    except Exception:
        return HTMLResponse(
            f"""<html><body style='font-family:monospace;padding:2rem;background:#111;color:#eee'>
            <h2>⚡ FastReact Dev Mode</h2>
            <p>Vite dev server not running on port {port}.</p>
            <p>Run: <code>cd frontend && npm run dev</code></p>
            </body></html>""",
            status_code=503
        )