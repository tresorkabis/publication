#!/bin/bash
# Script pour réinitialiser la base de données et générer les migrations
# Utilisation : ./reset_and_migrate.sh

set -e  # Arrêter en cas d'erreur

# Couleurs pour la sortie
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Pas de couleur

echo -e "${YELLOW}=== Réinitialisation de la base de données et des migrations ESFORCA ===${NC}"

# 1. Supprimer la base de données SQLite
if [ -f "db.sqlite3" ]; then
    echo -e "${YELLOW}Suppression de la base de données : db.sqlite3${NC}"
    rm -f db.sqlite3
    echo -e "${GREEN}Base de données supprimée avec succès.${NC}"
else
    echo -e "${YELLOW}Base de données non trouvée : db.sqlite3${NC}"
fi

# 2. Supprimer les anciennes migrations (sauf __init__.py)
echo -e "${YELLOW}Suppression des anciennes migrations...${NC}"
if [ -d "app/migrations" ]; then
    # Supprimer tous les fichiers .py sauf __init__.py
    find app/migrations -name "*.py" -not -name "__init__.py" -exec rm -f {} \;
    echo -e "${GREEN}Anciennes migrations supprimées.${NC}"
else
    echo -e "${YELLOW}Répertoire des migrations non trouvé : app/migrations${NC}"
fi

# 3. Générer les migrations
echo -e "${GREEN}Génération des nouvelles migrations...${NC}"
python manage.py makemigrations

# 4. Appliquer les migrations
echo -e "${GREEN}Application des migrations...${NC}"
python manage.py migrate

# 5. Générer les données de démonstration
echo -e "${GREEN}Génération des données de démonstration...${NC}"
python manage.py seed_demo_data

echo -e "${GREEN}=== Réinitialisation et migration terminées avec succès ===${NC}"
echo -e "${GREEN}Vous pouvez maintenant démarrer le serveur avec : ./run.sh start${NC}"
echo -e ""
echo -e "${YELLOW}=== Comptes de démonstration (mot de passe : demo) ===${NC}"
echo -e "  Super Admin : admin@esforca.cd"
echo -e "  Admin       : admin2@esforca.cd"
echo -e "  Secrétaire  : secretaire@esforca.cd"
echo -e "  Chef filière: chef.inf@esforca.cd"
echo -e "  Enseignant  : enseignant.inf1@esforca.cd"
echo -e "  Étudiant    : etudiant.inf.1@esforca.cd"