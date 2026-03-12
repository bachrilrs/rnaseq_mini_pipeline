FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/
COPY config.yaml .

# Install dependencies + package
RUN pip install --no-cache-dir -e ".[dev]"

# Run tests
CMD ["python", "-m", "rnaseq.pipeline"]