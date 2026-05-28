import os
import subprocess
import sys
import time
from backend.main import app  # Export app for direct ASGI runners if ever queried


def main():
    """Launch both backend API and frontend Streamlit concurrently."""
    # 1. Start the FastAPI backend on port 8000 in a background process
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    print("🚀 Starting FastAPI backend on port 8000...", flush=True)
    backend_process = subprocess.Popen(backend_cmd)

    # Give the backend a brief moment to start up
    time.sleep(3)

    # 2. Start the Streamlit frontend on the port dynamically assigned by the host ($PORT)
    port = os.getenv("PORT", "8501")
    print(f"🛍️ Starting Streamlit frontend on port {port}...", flush=True)

    streamlit_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port",
        port,
        "--server.address",
        "0.0.0.0",
    ]

    try:
        # Run Streamlit in the foreground (blocks until interrupted)
        subprocess.run(streamlit_cmd, check=True)
    except KeyboardInterrupt:
        print("Stopping servers...", flush=True)
    finally:
        # Ensure the backend process is cleaned up when exiting
        backend_process.terminate()


if __name__ == "__main__":
    main()
