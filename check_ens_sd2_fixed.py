#!/usr/bin/env python
"""Vérifie si le compte ens_sd2 existe et affiche ses informations"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from app.models import Personnel

User = get_user_model()

# Rechercher l'utilisateur ens_sd2
try:
    user = User.objects.get(username='ens_sd2')
    print("\n" + "="*70)
    print("COMPTE ENSEIGNANT: ens_sd2")
    print("="*70)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Nom complet: {user.get_full_name()}")
    print(f"Prénom: {user.prenom}")
    print(f"Nom: {user.nom}")
    
    # Vérifier si c'est un personnel (enseignant)
    try:
        personnel = Personnel.objects.get(user=user)
        print(f"\nInformations Enseignant:")
        print(f"  Grade: {personnel.grade}")
        print(f"  Fonction: {personnel.fonction}")
    except Personnel.DoesNotExist:
        print("\n⚠️ Ce compte n'est pas lié à un profil enseignant")
    
    print("\n" + "="*70)
    print("MOT DE PASSE:")
    print("  Le mot de passe par défaut pour tous les comptes est: demo")
    print("="*70)
    
except User.DoesNotExist:
    print("\n❌ Le compte 'ens_sd2' n'existe pas dans la base de données.")
    print("\nRecherche d'utilisateurs similaires...")
    
    # Chercher des utilisateurs avec des noms similaires
    similar = User.objects.filter(username__icontains='sd')
    if similar.exists():
        print("\nUtilisateurs trouvés avec 'sd' dans le nom:")
        for u in similar:
            print(f"  - {u.username}")
    else:
        print("Aucun utilisateur avec 'sd' dans le nom")
    
    # Afficher tous les personnels
    print("\nListe de tous les enseignants (Personnel):")
    personnels = Personnel.objects.all()
    for p in personnels:
        print(f"  - {p.user.username} ({p.user.get_full_name()}) - {p.grade}")