FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gfortran \
    make \
    libpq-dev \
    postgresql-client \
    r-base \
    r-base-dev \
    r-cran-ggplot2 \
    r-cran-tidyr \
    && rm -rf /var/lib/apt/lists/*

COPY data /app/data/
COPY r /app/r/
COPY sql /app/sql/
COPY pyproject.toml .
COPY src/ ./src/
COPY entrypoint.sh .
COPY config.yaml .

RUN pip install --no-cache-dir -e ".[dev]"
RUN chmod +x entrypoint.sh
RUN mkdir -p /app/output

CMD ["./entrypoint.sh"]