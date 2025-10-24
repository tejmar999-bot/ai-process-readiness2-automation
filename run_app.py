#!/usr/bin/env python3
"""
run_app.py — Start Streamlit on the first available port (8501..8510).
Prints helpful preview URLs for common cloud dev environments (Replit, Codespaces).
"""

import socket
import subprocess
import os
import sys
import urllib.parse

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
    """Try to construct the Replit preview URL."""
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
    """Provide a hint for Codespaces preview."""
    codespace = os.environ.get("CODESPACE_NAME") or os.environ.get("GITHUB_CODESPACE")
    gh_repo = os.environ.get("GITHUB_REPOSITORY")
    if codespace:
        example = f"https://{codespace}-{port}.githubpreview.dev"
        if gh_repo:
            example += f"  (repo: {gh_repo})"
        return example
    return None

def main():
    port = find_free_port(8501, 8510)
    if port is None:
        print("❌ No free port found between 8501–8510.", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Starting Streamlit on port {port} (auto-selected if 8501 was busy).")
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)

    print("\n🔗 Access URLs:")
    print(f"  • Local: http://localhost:{port}")
    print(f"  • Network: http://0.0.0.0:{port}")

    replit_preview = get_replit_preview(port)
    if replit_preview:
        print(f"  • Replit preview: {replit_preview}")

    codespaces_preview = get_codespaces_preview(port)
    if codespaces_preview:
        print(f"  • Codespaces preview: {codespaces_preview}")
        print("    (If using Codespaces, open the 'Ports' tab for the forwarded URL.)")

    if not replit_preview and not codespaces_preview:
        print("  • Tip: Check your platform’s 'Preview' or 'Ports' tab for a public URL.\n")

    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", str(port)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit exited with code {e.returncode}", file=sys.stderr)

if __name__ == "__main__":
    main()
