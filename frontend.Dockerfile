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

# Copy core frontend UI files
COPY frontend/ ./frontend/

# Expose Streamlit default port
EXPOSE 8501

# Launch Streamlit using uv runner, binding to all interfaces on port 8501
CMD ["uv", "run", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
