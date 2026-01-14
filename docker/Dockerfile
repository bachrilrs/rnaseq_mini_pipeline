FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base r-base-dev \
    build-essential \
    git \
    curl wget ca-certificates \
    libcurl4-openssl-dev libssl-dev libxml2-dev \
    libgit2-dev \
    pandoc \
    unzip tar gzip \
    locales \
 && rm -rf /var/lib/apt/lists/*

# (Optionnel) locale UTF-8, évite certaines erreurs RMarkdown
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8


COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt


RUN R -q -e "install.packages(c('BiocManager','jsonlite','rmarkdown','knitr','ggplot2','data.table'), repos='https://cloud.r-project.org')" \
 && R -q -e "BiocManager::install(c('DESeq2'), ask=FALSE, update=FALSE)" \
 && R -q -e "install.packages('tinytex', repos='https://cloud.r-project.org')" \
 && R -q -e "tinytex::install_tinytex(force=TRUE)" \
 && R -q -e "tinytex::tlmgr_update()" \
 && R -q -e "tinytex::tlmgr_install(c('latexmk','xetex','ec','fancyhdr','framed','titling','ifmtarg'))"


COPY src /app/src
COPY r /app/r
COPY sql /app/sql


# Make your package importable (si tu as un packaging propre)
# Alternative simple: PYTHONPATH sur /app/src
ENV PYTHONPATH=/app/src