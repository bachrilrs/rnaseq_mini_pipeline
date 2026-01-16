FROM python:3.11-slim 
# don't generate .pyc files and don't buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#everything will be run from /app
WORKDIR /app  

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY pyproject.toml /app/pyproject.toml
COPY src/ /app/src/

WORKDIR /app
COPY . /app
# Install the package
RUN pip install --upgrade pip setuptools \
  && pip install --no-cache-dir .

# Copy config and create output directory
COPY config.yaml /app/config.yaml
RUN mkdir -p /app/output

# Set the default command to run the pipeline
CMD ["python", "-m", "rnaseq.pipeline", "--config", "/app/config.yml"]
