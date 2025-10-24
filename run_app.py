cat > run_app.py <<'PY'
#!/usr/bin/env python3
"""
run_app.py — Start Streamlit on the first available port (8501..8510).
Prints helpful preview URLs for Replit/Codespaces and auto-opens the browser on local dev.
"""

import socket
import subprocess
import os
import sys
import urllib.parse
import time
import threading
import webbrowser

def find_free_port(start=8501, end=8510):
    """Return the first free port in the given range."""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    return None

def get_replit_preview(port: int) -> str | None:
    owner = os.environ.get("REPL_OWNER") or os.environ.get("REPLIT_OWNER")
    slug = os.environ.get("REPL_SLUG") or os.environ.get("REPLIT_SLUG")
    if owner and slug:
        return f"https://{slug}.{owner}.repl.co"
    replit_url = os.environ.get("REPLIT_URL") or os.environ.get("REPLIT_HOST")
    if replit_url:
        parsed = urllib.parse.urlparse(replit_url)
        if not parsed.scheme:
            replit_url = "https://" + replit_url
        return replit_url.rstrip("/")
    return None

def get_codespaces_preview(port: int) -> str | None:
    codespace = os.environ.get("CODESPACE_NAME") or os.environ.get("GITHUB_CODESPACE")
    gh_repo = os.environ.get("GITHUB_REPOSITORY")
    if codespace:
        example = f"https://{codespace}-{port}.githubpreview.dev"
        if gh_repo:
            example += f"  (repo: {gh_repo})"
        return example
    return None

def _is_local_desktop() -> bool:
    """
    Heuristic to detect a local desktop environment:
    - Not running in Replit or Codespaces
    - Not in common CI env vars
    - Has a DISPLAY (on Linux) or running on macOS/Windows (sys.platform)
    """
    if os.environ.get("REPL_OWNER") or os.environ.get("REPL_SLUG"):
        return False
    if os.environ.get("CODESPACE_NAME") or os.environ.get("GITHUB_CODESPACE"):
        return False
    # common CI markers
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS") or os.environ.get("GITLAB_CI"):
        return False
    # If running on Windows or macOS assume desktop
    if sys.platform.startswith("darwin") or sys.platform.startswith("win"):
        return True
    # On Linux, require DISPLAY or WAYLAND_DISPLAY
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return True
    return False

def _open_browser_later(url: str, delay: float = 2.5):
    """Open default browser after a small delay so Streamlit can bind the port."""
    def _open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
        except Exception:
            # best-effort, not fatal
            print(f"Could not open browser automatically. Open this URL manually: {url}")
    t = threading.Thread(target=_open, daemon=True)
    t.start()

def main():
    port = find_free_port(8501, 8510)
    if port is None:
        print("❌ No free port found between 8501–8510.", file=sys.stderr)
        sys.exit(1)

    local_url = f"http://localhost:{port}"
    network_url = f"http://0.0.0.0:{port}"

    print(f"🚀 Starting Streamlit on port {port} (auto-selected if 8501 was busy).")
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)

    print("\n🔗 Access URLs:")
    print(f"  • Local: {local_url}")
    print(f"  • Network: {network_url}")

    replit_preview = get_replit_preview(port)
    if replit_preview:
        print(f"  • Replit preview: {replit_preview}")

    codespaces_preview = get_codespaces_preview(port)
    if codespaces_preview:
        print(f"  • Codespaces preview: {codespaces_preview}")
        print("    (If using Codespaces, open the 'Ports' tab for the forwarded URL.)")

    if not replit_preview and not codespaces_preview:
        print("  • Tip: Check your platform’s 'Preview' or 'Ports' tab for a public URL.\n")

    # If this is likely a local desktop, schedule a browser open so the user doesn't have to copy-paste.
    if _is_local_desktop():
        print("⏱ Auto-opening your browser in a few seconds...")
        _open_browser_later(local_url)

    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", str(port)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit exited with code {e.returncode}", file=sys.stderr)

if __name__ == "__main__":
    main()
PY

chmod +x run_app.py
