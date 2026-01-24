FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Installation des dépendances système (Indispensable pour pandas/scikit-learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Installation de R et des packages Bioconductor nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    libxml2-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages('BiocManager', repos='https://cloud.r-project.org/')" \
    && R -e "BiocManager::install(c('edgeR', 'limma'), update = FALSE, ask = FALSE)"
# 2. Copie des fichiers nécessaires au build
COPY pyproject.toml .
COPY src/ ./src/

# 3. Installation du projet (C'est ici que ça échouait)
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# 4. Copie du reste (config, scripts)
COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]