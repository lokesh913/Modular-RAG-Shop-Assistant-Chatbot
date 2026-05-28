import os
import uvicorn


def main():
    """Launch the backend API server with dynamic host and port binding."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    # Disable reload in production environment (when PORT is specified by a cloud host)
    reload = os.getenv("PORT") is None
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
