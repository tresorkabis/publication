#!/usr/bin/env python
"""Vérifie et crée la filière Informatique si elle n'existe pas"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Filiere, Promotion, Cours

print("\n" + "="*60)
print("VÉRIFICATION DES FILIÈRES")
print("="*60)

# Vérifier si la filière Informatique existe
filiere_info = Filiere.objects.filter(code="INFO").first()

if not filiere_info:
    print("\n❌ La filière 'Informatique' n'existe pas.")
    print("   Création en cours...")
    
    filiere_info = Filiere.objects.create(
        code="INFO",
        libelle="Informatique",
        description="Licence en Informatique"
    )
    print(f"   ✅ Filière créée: {filiere_info.libelle} ({filiere_info.code})")
    
    # Créer une promotion par défaut
    promotion = Promotion.objects.create(
        filiere=filiere_info,
        libelle="L1"
    )
    print(f"   ✅ Promotion créée: {promotion.libelle}")
    
    # Créer quelques cours par défaut
    cours_data = [
        ("ALG101", "Algorithmique et Structures de Données", 3),
        ("PROG101", "Programmation Python", 3),
        ("MATH101", "Mathématiques pour l'Informatique", 2),
    ]
    
    for code, libelle, credits in cours_data:
        cours = Cours.objects.create(
            filiere=filiere_info,
            code=code,
            libelle=libelle,
            credit=credits,
            volume_horaire=45
        )
        print(f"   ✅ Cours créé: {cours.libelle}")
else:
    print(f"\n✅ La filière 'Informatique' existe déjà!")
    print(f"   Code: {filiere_info.code}")
    print(f"   Libellé: {filiere_info.libelle}")
    
    # Afficher les promotions et cours
    promotions = Promotion.objects.filter(filiere=filiere_info)
    print(f"\n   Promotions ({promotions.count()}):")
    for p in promotions:
        print(f"     - {p.libelle}")
    
    cours = Cours.objects.filter(filiere=filiere_info)
    print(f"\n   Cours ({cours.count()}):")
    for c in cours:
        print(f"     - {c.libelle} ({c.code})")

# Afficher toutes les filières
print("\n" + "-"*60)
print("TOUTES LES FILIÈRES:")
print("-"*60)
all_filieres = Filiere.objects.all()
print(f"Nombre total: {all_filieres.count()}\n")
for f in all_filieres:
    print(f"  - {f.libelle} (Code: {f.code})")

print("="*60 + "\n")