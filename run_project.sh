#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}RNA-SEQ PIPELINE${NC}"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Error: Docker not installed${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Docker not running${NC}"
    exit 1
fi

# Create .env if missing
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
else
    echo -e "${GREEN}✓ .env exists${NC}"
fi
echo ""

# Ask about cleanup (default: NO)
read -p "$(echo -e ${YELLOW}Remove old containers and volumes? \(y/N\)${NC}) " -n 1 -r
echo ""
REPLY=${REPLY:-N}
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing containers and volumes...${NC}"
    docker compose down -v 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✓ Cleanup complete${NC}"
else
    echo -e "${YELLOW}Keeping existing data${NC}"
fi
echo ""

# Ask about rebuild (default: YES)
read -p "$(echo -e ${YELLOW}Rebuild Docker image? \(Y/n\)${NC}) " -n 1 -r
echo ""
REPLY=${REPLY:-Y}
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Building image (no cache)...${NC}"
    docker compose build --no-cache
    echo -e "${GREEN}✓ Build complete${NC}"
else
    echo -e "${YELLOW}Using existing image${NC}"
fi
echo ""


# Start services with healthcheck
echo -e "${YELLOW}Starting services...${NC}"
docker compose up -d db
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
docker compose exec -T db pg_isready -U rnaseq_user -d rnaseq_db || sleep 10
echo -e "${GREEN}✓ Database ready${NC}"
echo ""

# Run pipeline
echo -e "${YELLOW}Running RNA-seq pipeline...${NC}"
docker compose run --rm pipeline

echo ""
echo -e "${GREEN}✓ Pipeline complete${NC}"
echo ""

# Open interactive bash
echo -e "${CYAN}Opening interactive shell (type 'exit' to stop)...${NC}"
echo -e "${YELLOW}Try:${NC}"
echo -e "  psql -h db -U rnaseq_user -d rnaseq_db"
echo ""

docker compose run --rm -it pipeline /bin/bash