import uvicorn


def main():
    """Launch the backend API server."""
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
