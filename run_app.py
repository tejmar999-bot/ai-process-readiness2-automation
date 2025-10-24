#!/usr/bin/env python3
"""
run_app.py — Start Streamlit on the first available port (8501..8510).
Safe for local dev; Cloud keeps 8501 fixed.
"""

import socket
import subprocess
import os
import sys

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

def main():
    port = find_free_port(8501, 8510)
    if port is None:
        print("❌ No free port found between 8501–8510. Please free one or edit this script.", file=sys.stderr)
        sys.exit(1)

    print(f"🚀 Starting Streamlit on port {port} (auto-selected if 8501 was in use).")
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)

    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", str(port)]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Streamlit exited with code {e.returncode}", file=sys.stderr)

if __name__ == "__main__":
    main()
