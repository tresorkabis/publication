#!/usr/bin/env python
"""
Script pour créer un compte étudiant de démonstration
Usage: python create_demo_student.py
"""

import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from app.models import Etudiant, Role, UtilisateurRole, Filiere, Promotion, Inscription, Cours, Evaluation, Cotation, TypeEvaluation
from decimal import Decimal
import random

User = get_user_model()

def create_demo_student():
    """Crée un compte étudiant de démonstration avec données réalistes"""
    
    print("=" * 60)
    print("CRÉATION D'UN COMPTE ÉTUDIANT DE DÉMONSTRATION")
    print("=" * 60)
    
    # Vérifier si l'étudiant existe déjà
    username = "etudiant_demo"
    if User.objects.filter(username=username).exists():
        print(f"\n⚠️  Le compte '{username}' existe déjà !")
        user = User.objects.get(username=username)
        etudiant = Etudiant.objects.get(user=user)
        print(f"   Nom: {user.get_full_name()}")
        print(f"   Email: {user.email}")
        print(f"   Mot de passe: demo123")
        return user, etudiant
    
    # Créer l'utilisateur
    print("\n📝 Création de l'utilisateur...")
    user = User.objects.create_user(
        username=username,
        email="etudiant.demo@university.com",
        password="demo",
        nom="Mbuyi",
        postnom="Winny",
        prenom="Grace",
        sexe="F",
        tel="+243 812 345 678",
        mat="ETU2024001",
        is_active=True,
        is_validated=True
    )
    print(f"   ✓ Utilisateur créé: {user.get_full_name()}")
    
    # Créer le profil étudiant
    print("\n🎓 Création du profil étudiant...")
    etudiant = Etudiant.objects.create(
        user=user,
        matricule="ETU2024001"
    )
    print(f"   ✓ Profil étudiant créé avec matricule: {etudiant.matricule}")
    
    # Assigner le rôle étudiant
    print("\n👤 Attribution du rôle étudiant...")
    role_etudiant, _ = Role.objects.get_or_create(libelle='etudiant')
    UtilisateurRole.objects.get_or_create(user=user, role=role_etudiant)
    print(f"   ✓ Rôle 'etudiant' attribué")
    
    # Mettre à jour le mot de passe pour s'assurer qu'il est bien "demo"
    user.set_password("demo")
    user.save()
    
    # Récupérer ou créer une filière et promotion
    print("\n📚 Attribution à une filière et promotion...")
    filiere, _ = Filiere.objects.get_or_create(
        code="INFO",
        defaults={
            'libelle': 'Informatique',
            'description': 'Licence en Informatique'
        }
    )
    print(f"   ✓ Filière: {filiere.libelle}")
    
    promotion, _ = Promotion.objects.get_or_create(
        filiere=filiere,
        libelle="L1"
    )
    print(f"   ✓ Promotion: {promotion.libelle}")
    
    # Créer l'inscription
    print("\n📋 Création de l'inscription...")
    inscription = Inscription.objects.create(
        etudiant=etudiant,
        promotion=promotion,
        annee="2024-2025",
        est_validee=True
    )
    print(f"   ✓ Inscription créée pour l'année {inscription.annee}")
    
    # Créer des cours et évaluations de démonstration
    print("\n📖 Création de cours et évaluations de démonstration...")
    
    # Créer quelques cours
    cours_data = [
        ("ALG101", "Algorithmique et Structures de Données", 3),
        ("PROG101", "Programmation Python", 3),
        ("MATH101", "Mathématiques pour l'Informatique", 2),
    ]
    
    cours_crees = []
    for code, libelle, credits in cours_data:
        cours, _ = Cours.objects.get_or_create(
            filiere=filiere,
            code=code,
            defaults={
                'libelle': libelle,
                'credit': credits,
                'volume_horaire': 45
            }
        )
        cours_crees.append(cours)
        print(f"   ✓ Cours: {cours.libelle}")
    
    # Créer des évaluations et notes
    print("\n📝 Création d'évaluations et notes de démonstration...")
    
    type_examen, _ = TypeEvaluation.objects.get_or_create(libelle="Examen")
    
    for cours in cours_crees:
        # Créer une évaluation
        evaluation = Evaluation.objects.create(
            type_evaluation=type_examen,
            cours=cours,
            date="2024-12-15",
            coefficient=1,
            is_published=True,
            published_at="2024-12-20T10:00:00"
        )
        print(f"   ✓ Évaluation créée: {evaluation}")
        
        # Créer quelques notes aléatoires
        note = Decimal(str(random.uniform(8, 18)))
        cotation = Cotation.objects.create(
            etudiant=etudiant,
            evaluation=evaluation,
            note=round(note, 2)
        )
        print(f"     → Note: {cotation.note}/20")
    
    print("\n" + "=" * 60)
    print("✅ COMPTE ÉTUDIANT CRÉÉ AVEC SUCCÈS !")
    print("=" * 60)
    print("\n📋 INFORMATIONS DE CONNEXION:")
    print(f"   Nom d'utilisateur: {user.username}")
    print(f"   Mot de passe: demo")
    print(f"   Nom complet: {user.get_full_name()}")
    print(f"   Email: {user.email}")
    print(f"   Matricule: {etudiant.matricule}")
    print(f"   Filière: {filiere.libelle}")
    print(f"   Promotion: {promotion.libelle}")
    print("\n🌐 Accédez à l'application avec ces identifiants")
    print("=" * 60)
    
    return user, etudiant

if __name__ == "__main__":
    try:
        create_demo_student()
    except Exception as e:
        print(f"\n❌ Erreur lors de la création du compte: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)