#!/usr/bin/env python
"""Liste toutes les filières"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Filiere

print("\n" + "="*60)
print("LISTE DES FILIÈRES")
print("="*60)

filieres = Filiere.objects.all()
count = filieres.count()

if count == 0:
    print("\n❌ Aucune filière enregistrée dans la base de données.")
    print("   La filière 'Informatique' n'existe pas.")
else:
    print(f"\n✅ Nombre de filières: {count}\n")
    for f in filieres:
        print(f"  - {f.libelle} (Code: {f.code})")

print("="*60 + "\n")