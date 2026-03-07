import traceback
from pathlib import Path

from .utils import build_traceback_html, NOT_FOUND_PAGE, NOT_ALLOWED_PAGE, is_browser_request

try:
    from flask import Flask, send_from_directory, request as flask_request
except ImportError:
    raise ImportError("Flask is not installed. Run: pip install flask")


class FlaskReact:
    """
    FlaskReact — Flask + React unified stack.

    Route rules:
      - Routes WITH react_prefix (default /api/) → React page routes
          • Browser request  → serves index.html → React Router renders
          • Non-browser      → 405 Not Allowed
          • Unregistered     → 404
      - Routes WITHOUT react_prefix → normal Flask routes
          • Work exactly like regular Flask
          • Accessible by everyone

    Usage:
        app = FlaskReact()

        # React page route — browser only
        @app.route("/api/users")
        def users_page(): pass

        # Normal route — everyone
        @app.route("/data/users")
        def get_users():
            return {"users": [...]}

        app.run()

    Custom prefix:
        app = FlaskReact(react_prefix="/ui/")
    """

    def __init__(
        self,
        react_dir: str = "frontend",
        build_dir: str = "frontend_build",
        traceback_overlay: bool = True,
        title: str = "FlaskReact App",
        react_prefix: str = "/api/",
    ):
        self.react_dir = Path(react_dir)
        self.build_dir = Path(build_dir)
        self.traceback_overlay = traceback_overlay
        # auto normalize: "ui/" → "/ui/" , "/ui" → "/ui/" , "ui" → "/ui/"
        react_prefix = react_prefix.strip("/")
        self.react_prefix = "/" + react_prefix + "/"
        self._react_page_routes: set[str] = set()

        self._app = Flask(title)

        self._setup_react_serving()

        if traceback_overlay:
            self._setup_traceback_overlay()

    def _is_react_route(self, path: str) -> bool:
        return path.startswith(self.react_prefix) or path == self.react_prefix.rstrip("/")

    def _setup_react_serving(self):
        """Serve React build + handle routing rules."""
        app = self._app
        build_dir = self.build_dir
        react_prefix = self.react_prefix
        react_page_routes = self._react_page_routes

        if build_dir.exists():

            @app.route("/")
            def serve_root():
                return send_from_directory(str(build_dir), "index.html")

            @app.route("/assets/<path:filename>")
            def serve_assets(filename):
                return send_from_directory(str(build_dir / "assets"), filename)

            @app.route("/<path:full_path>")
            def catch_all(full_path):
                path = "/" + full_path

                # ── React prefix route (/api/...) ─────────────────────
                if path.startswith(react_prefix) or path == react_prefix.rstrip("/"):

                    # Not registered → 404
                    if path not in react_page_routes:
                        return NOT_FOUND_PAGE.format(path=path), 404

                    # Registered — check if browser
                    accept = flask_request.headers.get("Accept", "")
                    if not is_browser_request(accept):
                        return NOT_ALLOWED_PAGE.format(path=path), 405

                    # Browser + registered → serve React
                    return send_from_directory(str(build_dir), "index.html")

                # ── Normal path — serve static or index.html ──────────
                # Try static file first
                static_file = build_dir / full_path
                if static_file.exists():
                    return send_from_directory(str(build_dir), full_path)

                # Fallback → index.html for React Router
                return send_from_directory(str(build_dir), "index.html")

        else:
            @app.route("/")
            def no_react():
                return """
                    <html><body style='font-family:monospace;padding:2rem;background:#111;color:#eee'>
                    <h2>⚡ FlaskReact Running</h2>
                    <p>No React build found.</p>
                    <p>Run: <code>cd frontend && npm run build</code></p>
                    </body></html>
                """

    def _setup_traceback_overlay(self):
        app = self._app

        @app.errorhandler(Exception)
        def handle_exception(exc):
            html = build_traceback_html(
                error_type=type(exc).__name__,
                error_message=str(exc),
                traceback_text=traceback.format_exc(),
                path=flask_request.path,
                framework="Flask",
            )
            return html, 500

    # ── Decorator delegation ──────────────────────────────────────────────

    def _register(self, path: str, **kwargs):
        """
        Core registration.
        Auto-normalizes path — adds leading slash if missing.
        React prefix routes → tracked, no-op handler (catch_all serves response).
        Normal routes → delegated to Flask directly.
        """
        # Auto-normalize: "data/status" → "/data/status"
        if not path.startswith("/"):
            path = "/" + path

        if self._is_react_route(path):
            self._react_page_routes.add(path)
            # Return a decorator that accepts the function but does nothing
            # catch_all in _setup_react_serving handles the actual response
            def decorator(f):
                return f  # return original function unchanged
            return decorator
        else:
            return self._app.route(path, **kwargs)

    def route(self, path: str, **kwargs):
        return self._register(path, **kwargs)

    def get(self, path: str, **kwargs):
        kwargs["methods"] = ["GET"]
        return self._register(path, **kwargs)

    def post(self, path: str, **kwargs):
        kwargs["methods"] = ["POST"]
        return self._register(path, **kwargs)

    def put(self, path: str, **kwargs):
        kwargs["methods"] = ["PUT"]
        return self._register(path, **kwargs)

    def delete(self, path: str, **kwargs):
        kwargs["methods"] = ["DELETE"]
        return self._register(path, **kwargs)

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False, **kwargs):
        print(f"""
⚡ FlaskReact running at http://{host}:{port}
   React UI  → http://{host}:{port}/
   API       → http://{host}:{port}/api/...
   React pages protected by prefix: {self.react_prefix}
        """)
        self._app.run(host=host, port=port, debug=debug, **kwargs)