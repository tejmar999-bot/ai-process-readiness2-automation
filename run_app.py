#!/usr/bin/env python3
import os, socket, subprocess, sys

def find_free_port(start=8501, end=8510):
    """Find the first available TCP port in the given range."""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("0.0.0.0", port)) != 0:
                return port
    raise RuntimeError("No free port found in range")

def main():
    port = find_free_port()
    print(f"🚀 Starting Streamlit on port {port}")
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"

    cmd = ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port", str(port)]
    print("\n🔗 Access URLs:")
    print(f"  • Local: http://localhost:{port}")
    print(f"  • Network: http://0.0.0.0:{port}")

    # Try to print Replit preview URL if environment vars exist
    owner = os.environ.get("REPL_OWNER") or os.environ.get("REPLIT_OWNER")
    slug = os.environ.get("REPL_SLUG") or os.environ.get("REPLIT_SLUG")
    domain = os.environ.get("REPLIT_DOMAINS") or os.environ.get("REPLIT_URL")
    if slug and owner:
        print(f"  • Replit preview: https://{slug}.{owner}.repl.co")
    elif domain:
        print(f"  • Replit preview (domain var): https://{domain.split(',')[0]}")
    else:
        print("  • (Replit preview: env vars not found — open via Preview panel)")

    print("\nPress Ctrl+C to stop.\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Stopped Streamlit app.")

if __name__ == "__main__":
    main()
