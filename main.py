import os
import uvicorn
from backend.main import app  # Export app for direct ASGI runners like uvicorn main:app


def main():
    """Launch the backend API server."""
    port = int(os.getenv("PORT", "8000"))
    # Bind to 0.0.0.0 to allow external network interface routing in docker containers
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
