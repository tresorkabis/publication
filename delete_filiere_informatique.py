#!/usr/bin/env python
"""Supprime la filière Informatique"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Filiere

print("\n" + "="*60)
print("SUPPRESSION DE LA FILIÈRE INFORMATIQUE")
print("="*60)

# Rechercher la filière Informatique
try:
    filiere = Filiere.objects.get(code='INFO')
    print(f"\n📋 Filière trouvée: {filiere.libelle} (Code: {filiere.code})")
    
    # Supprimer la filière
    filiere.delete()
    print(f"\n✅ Filière '{filiere.libelle}' supprimée avec succès!")
    
    # Vérifier le nombre de filières restantes
    count = Filiere.objects.count()
    print(f"\n📊 Nombre de filières restantes: {count}")
    
    # Afficher les filières restantes
    print("\nListe des filières restantes:")
    for f in Filiere.objects.all():
        print(f"  - {f.libelle} (Code: {f.code})")
    
except Filiere.DoesNotExist:
    print("\n❌ La filière 'Informatique' (INFO) n'existe pas dans la base de données.")
except Exception as e:
    print(f"\n❌ Erreur lors de la suppression: {str(e)}")

print("="*60 + "\n")