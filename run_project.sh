#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}RNA-SEQ PIPELINE${NC}"

# 1. Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo -e "${YELLOW}Please download and install Docker Desktop:${NC}"
    echo -e "${CYAN}🔗 https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi

# 2. Check if Docker Daemon is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is installed but not running.${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
    exit 1
fi

# 3. Environment Configuration (.env)
if [ ! -f .env ]; then
    echo -e "${YELLOW}Generating .env file...${NC}"
    cat <<EOF > .env
POSTGRES_DB=rnaseq_db
POSTGRES_USER=rnaseq_user
POSTGRES_PASSWORD=rnaseq_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATASET_ID=GSE60450
PIPELINE_VERSION=0.1.0
EOF
fi

# 4. Cleanup old containers
echo -e "${YELLOW}Cleaning up old containers...${NC}"
docker compose down -v 2>/dev/null || true

# 5. Start database
echo -e "${YELLOW}Starting PostgreSQL...${NC}"
docker compose up -d db
sleep 5

# 6. Run pipeline
echo -e "${YELLOW}Running RNA-seq pipeline...${NC}"
docker compose run --build --rm pipeline

echo -e "${GREEN}✓ Pipeline completed successfully at $(date)${NC}"