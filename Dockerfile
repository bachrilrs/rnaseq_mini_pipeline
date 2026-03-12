FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY pyproject .
RUN pip install --no-cache-dir -e .

# Copy code
COPY src/ ./src/
COPY config.yaml .

# Run pipeline
CMD ["python", "-m", "rnaseq.pipeline"]