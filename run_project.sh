#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}        RNA-SEQ PIPELINE : SYSTEM CHECK & LAUNCH        ${NC}"


# 1. OS Detection
OS_TYPE="$(uname -s)"

# 2. Check and Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    
    if [ "$OS_TYPE" == "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            read -p "Do you want to install Docker and Docker-Compose automatically? [Y/n] " confirm
            confirm=${confirm:-Y} # Default to Y
            
            if [[ $confirm =~ ^[Yy]$ ]]; then
                echo -e "${CYAN}Updating packages and installing Docker...${NC}"
                sudo apt-get update
                sudo apt-get install -y docker.io docker-compose
                sudo usermod -aG docker $USER
                echo -e "${GREEN}Installation complete!${NC}"
                echo -e "${YELLOW}IMPORTANT: Please log out and log back in (or restart your terminal) for group changes to take effect, then run this script again.${NC}"
                exit 0
            else
                echo -e "${RED}Installation cancelled. Please install Docker manually to continue.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}Automatic installation only supported on Debian/Ubuntu (apt). Please install Docker manually.${NC}"
            exit 1
        fi
    elif [ "$OS_TYPE" == "Darwin" ]; then
        echo -e "${YELLOW}For macOS: Please install Docker Desktop manually: https://www.docker.com/products/docker-desktop${NC}"
        exit 1
    fi
fi

# 3. Check if Docker Daemon is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker daemon is not running.${NC}"
    if [ "$OS_TYPE" == "Darwin" ]; then
        echo -e "${YELLOW}Please start Docker Desktop from your Applications.${NC}"
    else
        echo -e "${YELLOW}Try running: sudo systemctl start docker${NC}"
    fi
    exit 1
fi

# 4. Environment Configuration (.env)
if [ ! -f .env ]; then
    echo -e "${YELLOW}Checking configuration...${NC}"
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

# 5. Launch
echo -e "${YELLOW}Cleaning and building containers...${NC}"
docker-compose down -v > /dev/null 2>&1
docker-compose up -d db
docker-compose run --build --rm pipeline

echo -e "${GREEN}========================================================${NC}"
echo -e "${GREEN} Pipeline finished successfully at $(date)${NC}"
echo -e "${GREEN}========================================================${NC}"