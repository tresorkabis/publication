#!/bin/bash
# Script de lancement pour le projet ESFORCA
# Utilisation : ./run.sh [commande]
# Commandes disponibles : start, migrate, test, shell

set -e  # Arrêter en cas d'erreur

# Couleurs pour la sortie
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Pas de couleur

# Détection de l'environnement virtuel
if [ -d "venv" ]; then
    echo -e "${GREEN}Utilisation de l'environnement virtuel : venv${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}Utilisation de l'environnement virtuel : .venv${NC}"
    source .venv/bin/activate
elif python -c "import sys; print('Python disponible')" 2>/dev/null; then
    echo -e "${YELLOW}Attention : Aucun environnement virtuel détecté. Utilisation de Python système.${NC}"
else
    echo -e "${RED}Erreur : Python n'est pas disponible.${NC}"
    exit 1
fi

# Commande par défaut : démarrer le serveur
commande=${1:-"start"}

case $commande in
    "start")
        echo -e "${GREEN}Lancement du serveur de développement Django...${NC}"
        python manage.py runserver 0.0.0.0:8000
        ;;
    "migrate")
        echo -e "${GREEN}Application des migrations...${NC}"
        python manage.py migrate
        ;;
    "makemigrations")
        echo -e "${YELLOW}Création des migrations...${NC}"
        python manage.py makemigrations
        ;;
    "test")
        echo -e "${GREEN}Exécution des tests...${NC}"
        python manage.py test
        ;;
    "shell")
        echo -e "${GREEN}Ouverture de l'interpréteur Django...${NC}"
        python manage.py shell
        ;;
    "collectstatic")
        echo -e "${GREEN}Collecte des fichiers statiques...${NC}"
        python manage.py collectstatic --noinput
        ;;
    *)
        echo -e "${RED}Commande inconnue : $commande${NC}"
        echo "Commandes disponibles : start, migrate, makemigrations, test, shell, collectstatic"
        exit 1
        ;;
esac