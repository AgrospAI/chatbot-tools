FROM python:3.13-slim

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates build-essential
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install project dependencies
WORKDIR /app
COPY pyproject.toml /app/
COPY uv.lock /app/
COPY README.md /app/
ENV UV_NO_DEV=1
RUN uv sync --locked

# Copy application code
COPY fastrag /app/fastrag
COPY resources /app/resources

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run the application
CMD ["uv", "run", "fastrag", "serve", "--host", "0.0.0.0", "--port", "8000"]
