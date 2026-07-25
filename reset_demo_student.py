#!/usr/bin/env python
"""Supprime et recrée le compte étudiant de démonstration avec le mot de passe 'demo'"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from app.models import Etudiant, Inscription, Cotation, Evaluation, UtilisateurRole

User = get_user_model()

def reset_demo_student():
    """Supprime et recrée le compte étudiant de démonstration"""
    
    print("=" * 60)
    print("RÉINITIALISATION DU COMPTE ÉTUDIANT DE DÉMONSTRATION")
    print("=" * 60)
    
    # Supprimer l'ancien compte s'il existe
    username = "etudiant_demo"
    if User.objects.filter(username=username).exists():
        print(f"\n🗑️  Suppression de l'ancien compte '{username}'...")
        user = User.objects.get(username=username)
        
        # Supprimer les données liées
        etudiant = Etudiant.objects.filter(user=user).first()
        if etudiant:
            # Supprimer les cotations
            Cotation.objects.filter(etudiant=etudiant).delete()
            # Supprimer les inscriptions
            Inscription.objects.filter(etudiant=etudiant).delete()
            # Supprimer le profil étudiant
            etudiant.delete()
        
        # Supprimer les rôles utilisateur
        UtilisateurRole.objects.filter(user=user).delete()
        
        # Supprimer l'utilisateur
        user.delete()
        print(f"   ✓ Ancien compte supprimé")
    
    # Importer et exécuter le script de création
    print(f"\n📝 Création du nouveau compte avec mot de passe 'demo'...")
    from create_demo_student import create_demo_student
    create_demo_student()
    
    print("\n" + "=" * 60)
    print("✅ COMPTE RÉINITIALISÉ AVEC SUCCÈS !")
    print("=" * 60)
    print("\n🔐 IDENTIFIANTS DE CONNEXION:")
    print(f"   Nom d'utilisateur : etudiant_demo")
    print(f"   Mot de passe      : demo")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    try:
        reset_demo_student()
    except Exception as e:
        print(f"\n❌ Erreur lors de la réinitialisation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)