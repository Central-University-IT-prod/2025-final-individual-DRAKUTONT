# Stage 1: Install dependencies
FROM docker.io/python:3.11-alpine3.20 AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Setup env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Copy only pyproject.toml first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN uv sync

# Stage 2: Final image
FROM docker.io/python:3.11-alpine3.20

# Install runtime dependencies
RUN apk add --no-cache \
    tzdata \
    ca-certificates

# Set the working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY . .

# Create app user and set permissions
RUN adduser -D -g '' app && \
    chown -R app:app /app && \
    chmod -R 755 /app

# Run as non-root user
USER app

# Setup env vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PATH="/opt/venv/bin:$PATH"

# Expose port
EXPOSE 8080

# # Run gunicorn
# CMD ["gunicorn", \
#     "--bind", ":8080", \
#     "--timeout", "120", \
#     "--workers", "3", \
#     "ads_platform.wsgi:application"]
ENTRYPOINT ["sh", "-c", "./entrypoint.sh"]