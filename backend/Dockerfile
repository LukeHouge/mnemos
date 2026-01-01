FROM python:3.12-slim-bullseye

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy dependency files first
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-cache

# Copy application code
COPY . .

EXPOSE 8000

# Use uvicorn to run the application (production mode, no reload)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
