#!/usr/bin/env python
"""
Script pour réinitialiser tous les mots de passe vers 'demo'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import User

print("=" * 80)
print("RÉINITIALISATION DES MOTS DE PASSE")
print("=" * 80)

users = User.objects.all()
count = 0

for user in users:
    user.set_password('demo')
    user.save()
    count += 1
    print(f"✓ {user.username} - Mot de passe changé vers 'demo'")

print("\n" + "=" * 80)
print(f"RÉSUMÉ: {count} utilisateurs mis à jour")
print("=" * 80)
print("\nMot de passe par défaut pour tous les comptes: demo")
print("\nComptes enseignants avec cours:")
print("  - ens_math2 (Enseignant_MATH_2 Mukendi Anne)")
print("  - ens_gest1 (Enseignant_GEST_1 Kabila Jean)")
print("  - ens_gest2 (Enseignant_GEST_2 Mutombo Paul)")
print("\nAccès: http://localhost:8000/connexion/")