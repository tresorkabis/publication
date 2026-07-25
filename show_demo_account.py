#!/usr/bin/env python
"""Affiche les informations du compte étudiant de démonstration"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from app.models import Etudiant, Inscription

User = get_user_model()

try:
    user = User.objects.get(username='etudiant_demo')
    etudiant = Etudiant.objects.get(user=user)
    inscription = Inscription.objects.filter(etudiant=etudiant).first()
    
    print("\n" + "="*70)
    print(" "*20 + "COMPTE ÉTUDIANT DE DÉMONSTRATION")
    print("="*70)
    print("\n📋 IDENTIFIANTS DE CONNEXION:")
    print(f"   Nom d'utilisateur : {user.username}")
    print(f"   Mot de passe      : demo")
    print("\n👤 INFORMATIONS PERSONNELLES:")
    print(f"   Nom complet       : {user.get_full_name()}")
    print(f"   Email             : {user.email}")
    print(f"   Téléphone         : {user.tel or 'Non renseigné'}")
    print(f"   Sexe              : {user.get_sexe_display() if user.sexe else 'Non renseigné'}")
    print("\n🎓 INFORMATIONS ACADÉMIQUES:")
    print(f"   Matricule         : {etudiant.matricule}")
    if inscription:
        print(f"   Filière           : {inscription.promotion.filiere.libelle}")
        print(f"   Promotion         : {inscription.promotion.libelle}")
        print(f"   Année académique  : {inscription.annee}")
        print(f"   Inscription validée: {'Oui' if inscription.est_validee else 'Non'}")
    print("\n" + "="*70)
    print("   Utilisez ces identifiants pour vous connecter à l'application")
    print("="*70 + "\n")
    
except User.DoesNotExist:
    print("\n❌ Le compte étudiant de démonstration n'existe pas.")
    print("   Exécutez d'abord: python create_demo_student.py\n")
    sys.exit(1)