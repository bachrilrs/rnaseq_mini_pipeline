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
    echo -e "${YELLOW}Please download and install Docker Desktop for your OS:${NC}"
    echo -e "${CYAN}🔗 https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi

# 2. Check if Docker Daemon is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is installed but not running.${NC}"
    echo -e "${YELLOW}Action: Please start Docker Desktop and try again.${NC}"
    exit 1
fi

# 3. Environment Configuration (.env)
if [ ! -f .env ]; then
    echo -e "${YELLOW}Generating .env file...${NC}"
    if [ -f .env.template ]; then
        cp .env.template .env
    else
        cat <<EOF > .env
POSTGRES_DB=rnaseq_db
POSTGRES_USER=rnaseq_user
POSTGRES_PASSWORD=rnaseq_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOF
    fi
fi

# 4. Execution
echo -e "${YELLOW}Starting services...${NC}"

DOCKER_CMD="docker"
if ! docker ps > /dev/null 2>&1; then DOCKER_CMD="sudo docker"; fi

$DOCKER_CMD-compose down -v > /dev/null 2>&1
$DOCKER_CMD-compose up -d db
echo -e "${YELLOW}Building and running the Pipeline (R + Python)...${NC}"
$DOCKER_CMD-compose run --build --rm pipeline


echo -e "${GREEN} Pipeline finished successfully at $(date)${NC}"
