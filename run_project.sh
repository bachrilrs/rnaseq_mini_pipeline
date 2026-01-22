#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${YELLOW}Vérification de la configuration...${NC}"

if [ ! -f .env ]; then
    echo -e "${CYAN}Le fichier .env est absent.${NC}"
    
    if [ -f .env.template ]; then
        echo -e "${GREEN}Utilisation du template .env.template pour créer .env...${NC}"
        cp .env.template .env
    else
        echo -e "${YELLOW}Avertissement : .env.template absent. Création d'un fichier .env avec des valeurs par défaut.${NC}"
        cat <<EOF > .env
POSTGRES_DB=rnaseq_db
POSTGRES_USER=rnaseq_user
POSTGRES_PASSWORD=rnaseq_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATASET_ID=GSE60450
PIPELINE_VERSION=1.0.0
EOF
    fi
else
    echo -e "${GREEN}Fichier .env détecté.${NC}"
fi

# --- LA SUITE DU SCRIPT ---
echo -e "${YELLOW}Lancement de Docker...${NC}"
docker-compose down -v > /dev/null 2>&1
docker-compose up -d db
docker-compose run --build --rm pipeline

echo -e "${GREEN}Pipeline exécuté avec succès à $(date)${NC}"