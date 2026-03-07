import sys


TRACEBACK_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>FastReact Error</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #1a1a1a;
      color: #e0e0e0;
      font-family: 'Fira Code', 'Courier New', monospace;
      padding: 2rem;
    }}
    .header {{
      background: #c0392b;
      color: white;
      padding: 1rem 1.5rem;
      border-radius: 8px 8px 0 0;
      font-size: 1.1rem;
      font-weight: bold;
    }}
    .error-type {{
      background: #2d2d2d;
      border-left: 4px solid #c0392b;
      padding: 1rem 1.5rem;
      font-size: 1rem;
      color: #e74c3c;
    }}
    .traceback {{
      background: #242424;
      padding: 1.5rem;
      white-space: pre-wrap;
      font-size: 0.875rem;
      line-height: 1.6;
      border-radius: 0 0 8px 8px;
      border: 1px solid #333;
      color: #a8b5c8;
    }}
    .footer {{
      margin-top: 1rem;
      font-size: 0.75rem;
      color: #555;
      text-align: center;
    }}
    .pill {{
      display: inline-block;
      background: #2d2d2d;
      border: 1px solid #444;
      padding: 0.2rem 0.8rem;
      border-radius: 999px;
      font-size: 0.75rem;
      margin-right: 0.5rem;
      color: #aaa;
    }}
    .top-bar {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }}
  </style>
</head>
<body>
  <div class="top-bar">
    <span class="pill">⚡ FastReact</span>
    <span class="pill">🐍 Python {python_version}</span>
    <span class="pill">🌐 {path}</span>
    <span class="pill">{framework}</span>
  </div>
  <div class="header">
    <span>🔴</span> {framework} Traceback — {error_type}
  </div>
  <div class="error-type">
    {error_message}
  </div>
  <div class="traceback">{traceback_text}</div>
  <div class="footer">
    Powered by FastReact — Python errors served like React errors 🚀
  </div>
</body>
</html>"""


def build_traceback_html(
    error_type: str,
    error_message: str,
    traceback_text: str,
    path: str,
    framework: str = "FastAPI",
) -> str:
    """Render the traceback HTML overlay."""
    clean_tb = filter_traceback(traceback_text)
    return TRACEBACK_TEMPLATE.format(
        python_version=sys.version.split()[0],
        path=path,
        framework=framework,
        error_type=error_type,
        error_message=error_message,
        traceback_text=clean_tb,
    )


def filter_traceback(full_tb: str) -> str:
    """
    Filter traceback to show only user code.
    Removes internal framework lines from:
    - site-packages (starlette, fastapi, anyio, flask, werkzeug...)
    - fastreact internals
    - frozen modules
    """
    SKIP_PATTERNS = (
        "site-packages",
        "<frozen ",
        "fastreact\\core.py",
        "fastreact/core.py",
        "fastreact\\flask_core.py",
        "fastreact/flask_core.py",
    )

    lines = full_tb.splitlines()
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Always keep header line
        if line.startswith("Traceback"):
            result.append(line)
            i += 1
            continue

        # Final error line — no leading whitespace + has colon
        if not line.startswith(" ") and ":" in line:
            result.append(line)
            i += 1
            continue

        # File line — decide keep or skip
        if line.strip().startswith("File "):
            is_internal = any(pat in line for pat in SKIP_PATTERNS)
            if is_internal:
                # Skip this File line + all following code/caret lines
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip().startswith("File ") or (
                        not next_line.startswith(" ") and ":" in next_line
                    ):
                        break
                    i += 1
                continue
            else:
                result.append(line)
                i += 1
                # Keep code + caret lines that follow
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip().startswith("File ") or (
                        not next_line.startswith(" ") and ":" in next_line
                    ):
                        break
                    result.append(next_line)
                    i += 1
                continue

        result.append(line)
        i += 1

    # Safety: if filter removed everything, return full traceback
    if len(result) <= 2:
        return full_tb

    return "\n".join(result)


NOT_ALLOWED_PAGE = """<!DOCTYPE html>
<html>
<head><title>405 Not Allowed</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#1a1a1a; color:#e0e0e0; font-family:monospace; display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .box {{ background:#2d2d2d; border:1px solid #444; border-radius:12px; padding:2rem 3rem; text-align:center; }}
  .code {{ font-size:4rem; color:#e74c3c; }}
  .msg {{ color:#aaa; margin-top:0.5rem; }}
  .pill {{ display:inline-block; background:#1a1a1a; border:1px solid #e74c3c; color:#e74c3c; padding:0.2rem 0.8rem; border-radius:999px; font-size:0.75rem; margin-top:1rem; }}
</style></head>
<body>
  <div class="box">
    <div class="code">405</div>
    <h2>Not Allowed</h2>
    <p class="msg">{path} is a React route.<br>It can only be accessed from a browser.</p>
    <div class="pill">⚡ FastReact</div>
  </div>
</body>
</html>"""


NOT_FOUND_PAGE = """<!DOCTYPE html>
<html>
<head><title>404 Not Found</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#1a1a1a; color:#e0e0e0; font-family:monospace; display:flex; align-items:center; justify-content:center; min-height:100vh; }}
  .box {{ background:#2d2d2d; border:1px solid #444; border-radius:12px; padding:2rem 3rem; text-align:center; }}
  .code {{ font-size:4rem; color:#888; }}
  .msg {{ color:#aaa; margin-top:0.5rem; }}
  .pill {{ display:inline-block; background:#1a1a1a; border:1px solid #555; color:#888; padding:0.2rem 0.8rem; border-radius:999px; font-size:0.75rem; margin-top:1rem; }}
  a {{ color:#e74c3c; text-decoration:none; display:block; margin-top:1rem; }}
</style></head>
<body>
  <div class="box">
    <div class="code">404</div>
    <h2>Page Not Found</h2>
    <p class="msg">{path} is not a registered route.</p>
    <a href="/">← Go Home</a>
    <div class="pill">⚡ FastReact</div>
  </div>
</body>
</html>"""


def is_browser_request(accept_header: str) -> bool:
    """
    Detect if request is from a browser or a service like Postman/curl.
    Browsers send Accept: text/html
    Postman/curl/services send Accept: application/json or */*
    """
    if not accept_header:
        return False
    return "text/html" in accept_header