# Use a modern, light-weight Python base image
FROM python:3.12-slim

# Install uv (extremely fast and modern Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set Python environment flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set active working directory
WORKDIR /app

# Copy dependency specification files
COPY pyproject.toml uv.lock ./

# Install production dependencies deterministically using the lockfile
RUN uv sync --frozen --no-dev

# Copy core application files
COPY backend/ ./backend/
COPY data/ ./data/
COPY main.py ./main.py

# Expose backend default port
EXPOSE 8000

# Launch uvicorn server using uv runner, binding to all interfaces on port 8000
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
