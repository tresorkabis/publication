#!/usr/bin/env python
"""
Affiche les enseignants qui ont des cours assignés,
avec leur nom d'utilisateur et mot de passe.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Personnel, Cours, ProposalCoursEnseignant

print("=" * 70)
print("ENSEIGNANTS AYANT DES COURS ASSIGNES")
print("=" * 70)

enseignants = Personnel.objects.select_related('user').all()

trouve = False
for ens in enseignants:
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=ens,
        propositions_enseignants__est_accepte=True
    ).distinct()

    if cours_assignes.exists():
        trouve = True
        user = ens.user
        print(f"\n[Enseignant] : {user.get_full_name() or user.username}")
        print(f"   Nom d'utilisateur : {user.username}")
        print(f"   Mot de passe     : demo")
        print(f"   Grade            : {ens.grade}")
        print(f"   Cours ({cours_assignes.count()}) :")
        for c in cours_assignes:
            print(f"      - {c.libelle} ({c.code})")
        print("-" * 50)

if not trouve:
    print("\n[Aucun] enseignant avec des cours assignes trouve.")
    print("   Executez d'abord : python manage.py seed_demo_data\n")

print("=" * 70)
