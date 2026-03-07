import subprocess
import sys
import os
import re
import signal
import threading
import argparse
from pathlib import Path


BANNER = """
███████╗ █████╗ ███████╗████████╗██████╗ ███████╗ █████╗  ██████╗████████╗
██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝
█████╗  ███████║███████╗   ██║   ██████╔╝█████╗  ███████║██║        ██║   
██╔══╝  ██╔══██║╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║        ██║   
██║     ██║  ██║███████║   ██║   ██║  ██║███████╗██║  ██║╚██████╗   ██║   
╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   
                                                        
        FastAPI + React = One Unified Stack 🚀
"""


# ── Node helpers ─────────────────────────────────────────────────────────────

def get_version(cmd):
    for flag in ["--version", "-v", "-V"]:
        try:
            out = subprocess.check_output(
                [cmd, flag],
                stderr=subprocess.DEVNULL,
                shell=(sys.platform == "win32")
            ).decode().strip()
            if out:
                return out
        except Exception:
            continue
    return None


def auto_install_node():
    platform = sys.platform
    print("\n  🔧 Attempting to auto-install Node.js...\n")
    try:
        if platform == "win32":
            print("  📦 Using winget...")
            result = subprocess.run(
                ["winget", "install", "OpenJS.NodeJS.LTS",
                 "--accept-source-agreements", "--accept-package-agreements"],
                shell=True
            )
            if result.returncode == 0:
                print("\n  ✅ Node.js installed! Please reopen your terminal and run again.")
                return True
            raise Exception("winget failed")
        elif platform == "darwin":
            result = subprocess.run(["brew", "install", "node"])
            if result.returncode == 0:
                return True
            raise Exception("brew failed")
        elif platform.startswith("linux"):
            subprocess.run(["sudo", "apt", "update"], check=True)
            result = subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"])
            if result.returncode == 0:
                return True
            raise Exception("apt failed")
    except Exception as e:
        print(f"\n  ❌ Auto-install failed: {e}")
        print("  👉 Install manually from: https://nodejs.org")
        return False


def check_node(auto_install=True):
    node_version = get_version("node")
    npm_version = get_version("npm")
    if node_version and npm_version:
        print(f"  ✅ Node.js {node_version}")
        print(f"  ✅ npm v{npm_version}")
        return True
    print("  ❌ Node.js is not installed.")
    if auto_install:
        print("  💡 Attempting auto-install...\n")
        if auto_install_node():
            node_version = get_version("node")
            npm_version = get_version("npm")
            if node_version and npm_version:
                return True
        return False
    print("  👉 Install from: https://nodejs.org")
    return False


# ── Scaffold ─────────────────────────────────────────────────────────────────

def scaffold_react(project_name: str, target_dir: Path):
    print(BANNER)
    print(f"🛠️  Scaffolding React project: '{project_name}'")
    print(f"📁 Location: {target_dir / project_name}\n")
    print("🔍 Checking dependencies...")

    if not check_node(auto_install=True):
        sys.exit(1)

    react_path = target_dir / project_name
    is_windows = sys.platform == "win32"

    print(f"\n⚡ Running: npm create vite@latest {project_name} -- --template react\n")
    result = subprocess.run(
        ["npm", "create", "vite@latest", project_name, "--", "--template", "react"],
        cwd=str(target_dir),
        input=b"\n",
        shell=is_windows,
    )
    if result.returncode != 0:
        print("\n❌ Failed to scaffold React project.")
        sys.exit(1)

    print(f"\n📦 Installing npm dependencies...\n")
    result = subprocess.run(
        ["npm", "install"],
        cwd=str(react_path),
        shell=is_windows,
    )
    if result.returncode != 0:
        print("\n❌ Failed to install npm dependencies.")
        sys.exit(1)

    inject_vite_config(react_path)
    print_success(project_name, react_path)


def inject_vite_config(react_path: Path, extra_proxies: list[str] = None):
    """
    Write vite.config.js with proxy config.
    extra_proxies: list of path prefixes to proxy to FastAPI
                   e.g. ['/data', '/ui']
    """
    # Default proxies always included
    proxy_prefixes = ['/data', '/api', '/ui']

    if extra_proxies:
        for p in extra_proxies:
            if p not in proxy_prefixes:
                proxy_prefixes.append(p)

    # Build proxy entries
    proxy_entries = ""
    for prefix in proxy_prefixes:
        proxy_entries += f"""      '{prefix}': {{
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }},
"""

    config_content = f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'

// FastReact: Tunnels API/page calls from React dev server to FastAPI
export default defineConfig({{
  plugins: [react()],
  server: {{
    port: 5173,
    proxy: {{
{proxy_entries}    }}
  }},
  build: {{
    outDir: '../frontend_build',
    emptyOutDir: true,
  }}
}})
"""
    vite_config = react_path / "vite.config.js"
    with open(vite_config, "w") as f:
        f.write(config_content)
    print("  ✅ Injected FastReact proxy config into vite.config.js")


# ── Dev mode ─────────────────────────────────────────────────────────────────

VALID_UVICORN_OPTIONS = {
    "--host", "--port", "--reload", "--reload-delay", "--reload-dir",
    "--workers", "--log-level", "--access-log", "--no-access-log",
    "--use-colors", "--no-use-colors", "--proxy-headers",
    "--forwarded-allow-ips", "--root-path", "--limit-concurrency",
    "--limit-max-requests", "--timeout-keep-alive", "--ssl-keyfile",
    "--ssl-certfile", "--ssl-version", "--ssl-cert-reqs",
    "--ssl-ca-certs", "--ssl-ciphers", "--h11-max-incomplete-event-size",
    "--interface", "--http", "--ws", "--ws-max-size", "--ws-ping-interval",
    "--ws-ping-timeout", "--lifespan", "--env-file", "--app-dir",
    "--factory", "--loop", "--backlog",
}

def _validate_uvicorn_args(args: list[str]):
    """
    Check uvicorn args for typos before launching.
    Exits with a clear error message if invalid option found.
    """
    for arg in args:
        if arg.startswith("--"):
            # Strip value part e.g. --port=8000 → --port
            flag = arg.split("=")[0]
            if flag not in VALID_UVICORN_OPTIONS:
                # Find closest match
                import difflib
                close = difflib.get_close_matches(flag, VALID_UVICORN_OPTIONS, n=1, cutoff=0.6)
                suggestion = f"  Did you mean: {close[0]}" if close else ""
                print(f"""
╔══════════════════════════════════════════════╗
║         ❌ FastReact — Invalid Option        ║
╠══════════════════════════════════════════════╣
║                                              ║
║   Unknown option: {flag:<28}║
║   {suggestion:<46}║
║                                              ║
║   Run: fastreact dev --help                  ║
║                                              ║
╚══════════════════════════════════════════════╝
""")
                sys.exit(1)

def detect_react_dir(cwd: Path) -> Path | None:
    """Find the React project folder (contains package.json + vite.config.js)."""
    for candidate in ["frontend", "client", "web", "react-app"]:
        p = cwd / candidate
        if (p / "package.json").exists() and (p / "vite.config.js").exists():
            return p
    # fallback: any subfolder with vite.config.js
    for item in cwd.iterdir():
        if item.is_dir() and (item / "vite.config.js").exists():
            return item
    return None


def extract_prefixes_from_main(main_file: Path) -> list[str]:
    """
    Parse main.py to extract react_prefix and all route paths.
    Returns list of unique path prefixes to proxy.
    e.g. ['/data', '/ui', '/items']
    """
    prefixes = set()
    try:
        content = main_file.read_text()

        # Extract react_prefix value e.g. react_prefix="ui" or react_prefix="/api/"
        match = re.search(r'react_prefix\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            raw = match.group(1).strip("/")
            prefixes.add("/" + raw)

        # Extract all @app.get("/something/...") route prefixes
        for m in re.finditer(r'@app\.\w+\(["\'](/[^/"\']*)', content):
            segment = m.group(1)  # e.g. /data or /ui
            if segment and segment != "/":
                prefixes.add(segment)

    except Exception as e:
        print(f"  ⚠️  Could not parse {main_file.name}: {e}")

    return list(prefixes)


def run_dev(app_string: str, uvicorn_args: list[str], cwd: Path, show_calls: bool = False):
    """
    Start both Uvicorn and Vite dev server together.
    app_string: e.g. "main:app"
    uvicorn_args: extra args passed through e.g. ["--reload", "--port", "8000"]
    """
    print(BANNER)
    is_windows = sys.platform == "win32"

    # Parse port from uvicorn args
    port = "8000"
    if "--port" in uvicorn_args:
        port = uvicorn_args[uvicorn_args.index("--port") + 1]

    # Find React project dir
    react_dir = detect_react_dir(cwd)
    if not react_dir:
        print("❌ Could not find React project folder.")
        print("   Make sure you ran: fastreact create frontend")
        sys.exit(1)

    print(f"📁 React project: {react_dir.name}/")

    # Extract prefixes from main file and silently update vite.config.js
    main_file_name = app_string.split(":")[0] + ".py"
    main_file = cwd / main_file_name
    prefixes = extract_prefixes_from_main(main_file)

    if prefixes:
        print(f"  🔍 Detected route prefixes: {prefixes}")
        inject_vite_config(react_dir, extra_proxies=prefixes)
    else:
        inject_vite_config(react_dir)

    call_line = "║   📡  Call monitor  →  watching all requests          ║" if show_calls else "║   💡  Tip: add --call to monitor all requests           ║"

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                  ⚡ FastReact Dev Mode                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║   🌐  Open  →  http://localhost:5173                     ║
║                                                          ║
║   🐍  FastAPI  →  http://127.0.0.1:{port}                   ║
║   ⚛️   Vite     →  http://localhost:5173  (HMR on)       ║
║   🔀  Proxy    →  all routes tunneled                    ║
║                                                          ║
{call_line}
║                                                          ║
║   🛑  Ctrl+C to stop everything                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

    # Strip out fastreact-owned flags before validating uvicorn args
    # --call is ours, not uvicorn's
    FASTREACT_FLAGS = {"--call"}
    uvicorn_only_args = [a for a in uvicorn_args if a not in FASTREACT_FLAGS]

    # Validate uvicorn args before starting anything
    _validate_uvicorn_args(uvicorn_only_args)
    uvicorn_args = uvicorn_only_args

    # Always add --reload if not present
    uvicorn_cmd = ["uvicorn", app_string] + uvicorn_args
    if "--reload" not in uvicorn_args:
        uvicorn_cmd.append("--reload")

    # Filter output — only show errors + reload notices from uvicorn
    uvicorn_proc = subprocess.Popen(
        uvicorn_cmd,
        cwd=str(cwd),
        shell=is_windows,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Vite output fully suppressed — we show our own banner
    vite_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(react_dir),
        shell=is_windows,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Handle Ctrl+C — kill both cleanly
    def shutdown(sig=None, frame=None):
        print("\n\n🛑 Shutting down FastReact...")
        print("   ✅ Uvicorn stopped")
        print("   ✅ Vite stopped")
        try:
            uvicorn_proc.terminate()
            vite_proc.terminate()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, shutdown)

    # Stream uvicorn output — filter based on --call flag
    def stream_uvicorn():
        SHOW_ALWAYS = (
            "error", "Error", "ERROR",
            "Reloading", "reloading",
            "Application startup complete",
            "Traceback",
        )
        SKIP_PATTERNS = (
            "Will watch for changes",
            "Started reloader",
            "Started server process",
            "Waiting for application",
            "Uvicorn running on",
        )
        # HTTP method colors
        METHOD_COLORS = {
            "GET":    "\033[32m",   # green
            "POST":   "\033[34m",   # blue
            "PUT":    "\033[33m",   # yellow
            "DELETE": "\033[31m",   # red
            "PATCH":  "\033[35m",   # magenta
        }
        STATUS_COLORS = {
            "2": "\033[32m",   # 2xx green
            "3": "\033[36m",   # 3xx cyan
            "4": "\033[33m",   # 4xx yellow
            "5": "\033[31m",   # 5xx red
        }
        RESET = "\033[0m"
        BOLD  = "\033[1m"
        DIM   = "\033[2m"

        for line in uvicorn_proc.stdout:
            text = line.decode(errors="replace").rstrip()
            if not text:
                continue
            if any(skip in text for skip in SKIP_PATTERNS):
                continue

            # Always show errors/reloads
            if any(show in text for show in SHOW_ALWAYS):
                print(f"   {text}")
                continue

            # HTTP request lines e.g:
            # 127.0.0.1:PORT - "GET /api/users HTTP/1.1" 200 OK
            if show_calls and '" ' in text and "HTTP/" in text:
                try:
                    # Parse: IP - "METHOD PATH HTTP" STATUS
                    import re
                    m = re.search(r'"(\w+) ([^ ]+) HTTP/[\d.]+" (\d+)', text)
                    if m:
                        method  = m.group(1)
                        path    = m.group(2)
                        status  = m.group(3)

                        method_color = METHOD_COLORS.get(method, "\033[37m")
                        status_color = STATUS_COLORS.get(status[0], "\033[37m")

                        import datetime
                        ts = datetime.datetime.now().strftime("%H:%M:%S")

                        print(
                            f"  {DIM}{ts}{RESET}  "
                            f"{method_color}{BOLD}{method:<7}{RESET}  "
                            f"{path:<40}  "
                            f"{status_color}{BOLD}{status}{RESET}"
                        )
                    else:
                        print(f"   {text}")
                except Exception:
                    print(f"   {text}")

        print("\n⚠️  FastAPI server stopped. Press Ctrl+C to exit.")

    def watch_vite():
        vite_proc.wait()
        print("\n⚠️  Vite server stopped. Press Ctrl+C to exit.")

    t1 = threading.Thread(target=stream_uvicorn, daemon=True)
    t2 = threading.Thread(target=watch_vite, daemon=True)
    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        shutdown()


# ── Print success ─────────────────────────────────────────────────────────────

def print_success(project_name: str, react_path: Path):
    print(f"""
╔══════════════════════════════════════════════════════╗
║         ✅ FastReact scaffold complete!              ║
╚══════════════════════════════════════════════════════╝

📁 React project created at:
   {react_path}

🚀 Next steps:

   Dev mode (both servers at once):
      fastreact dev main:app --reload

   Or manually:
      uvicorn main:app --reload
      cd {project_name} && npm run dev

   Production build:
      cd {project_name} && npm run build

⚡ Powered by FastReact
""")


# ── CLI entry ─────────────────────────────────────────────────────────────────



HELP_TEXT = (
    "\033[1m\033[35m\n"
    "███████╗ █████╗ ███████╗████████╗██████╗ ███████╗ █████╗  ██████╗████████╗\n"
    "██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝\n"
    "█████╗  ███████║███████╗   ██║   ██████╔╝█████╗  ███████║██║        ██║   \n"
    "██╔══╝  ██╔══██║╚════██║   ██║   ██╔══██╗██╔══╝  ██╔══██║██║        ██║   \n"
    "██║     ██║  ██║███████║   ██║   ██║  ██║███████╗██║  ██║╚██████╗   ██║   \n"
    "\033[0m\n"
    "\033[2m        FastAPI + React = One Unified Stack\033[0m\n\n"
    "\033[1m\033[36m  COMMANDS\033[0m\n\n"
    "  \033[1m\033[32mfastreact create\033[0m \033[33m<name>\033[0m\n"
    "  \033[2m  Scaffold a Vite React app wired into your FastAPI project\033[0m\n\n"
    "    $ fastreact create frontend\n\n"
    "  \033[1m\033[32mfastreact dev\033[0m \033[33m<file:app>\033[0m \033[2m[options]\033[0m\n"
    "  \033[2m  Start FastAPI + Vite together. Same syntax as uvicorn.\033[0m\n\n"
    "    $ fastreact dev main:app --reload\n"
    "    $ fastreact dev main:app --reload --port 8000\n"
    "    $ fastreact dev main:app --reload --host 0.0.0.0\n"
    "    $ fastreact dev main:app --reload --call\n\n"
    "\033[1m\033[36m  UVICORN OPTIONS\033[0m\n\n"
    "  \033[33m--reload\033[0m              Auto-restart on file save\n"
    "  \033[33m--port\033[0m   \033[35m<number>\033[0m     Port number              \033[2mdefault: 8000\033[0m\n"
    "  \033[33m--host\033[0m   \033[35m<address>\033[0m    Host address             \033[2mdefault: 127.0.0.1\033[0m\n"
    "  \033[33m--workers\033[0m \033[35m<number>\033[0m    Worker processes         \033[2mdefault: 1\033[0m\n\n"
    "\033[1m\033[36m  FASTREACT FLAGS\033[0m\n\n"
    "  \033[33m--call\033[0m                Live monitor - every request colored by method and status\n\n"
    "\033[1m\033[36m  HOW ROUTING WORKS\033[0m\n\n"
    "  \033[32m@app.get(\"/ui/users\")\033[0m    React page  - browser gets React, Postman gets \033[31m405\033[0m\n"
    "  \033[32m@app.get(\"/data/users\")\033[0m  Normal route - everyone gets JSON             \033[32m200\033[0m\n\n"
    "\033[1m\033[36m  QUICK START\033[0m\n\n"
    "  fastreact create frontend\n"
    "  fastreact dev main:app --reload --call\n\n"
    "  \033[2m# build for prod\033[0m\n"
    "  cd frontend && npm run build\n"
    "  uvicorn main:app --host 0.0.0.0 --port 8000\n\n"
    "  \033[36m  pip install fastreact\033[0m\n"
)


def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ("--help", "-h", "help")):
        print(HELP_TEXT)
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", add_help=False)
    create_parser.add_argument("name")

    dev_parser = subparsers.add_parser("dev", add_help=False)
    dev_parser.add_argument("app")
    dev_parser.add_argument("uvicorn_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    cwd = Path(os.getcwd())

    if args.command == "create":
        scaffold_react(args.name, cwd)

    elif args.command == "dev":
        show_calls = "--call" in args.uvicorn_args
        uvicorn_args = [a for a in args.uvicorn_args if a != "--call"]
        run_dev(args.app, uvicorn_args, cwd, show_calls=show_calls)

    else:
        print(HELP_TEXT)


if __name__ == "__main__":
    main()