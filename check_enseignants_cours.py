#!/usr/bin/env python
"""
Script pour vérifier les enseignants et leurs cours assignés
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import *

print("=" * 80)
print("LISTE DES ENSEIGNANTS ET LEURS COURS ASSIGNÉS")
print("=" * 80)

enseignants = Personnel.objects.select_related('user').all()

for enseignant in enseignants:
    user = enseignant.user
    print(f"\n📚 Enseignant: {user.get_full_name()}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Fonction: {enseignant.fonction.intitule if enseignant.fonction else 'N/A'}")
    print(f"   Grade: {enseignant.grade}")
    
    # Récupérer les cours assignés (propositions acceptées)
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().select_related('filiere', 'semestre')
    
    if cours_assignes:
        print(f"   Cours assignés ({cours_assignes.count()}):")
        for cours in cours_assignes:
            print(f"      - {cours.libelle} ({cours.code}) - {cours.filiere.libelle} - {cours.semestre.libelle}")
    else:
        print(f"   Cours assignés: Aucun")
    
    # Vérifier les propositions en attente
    propositions_en_attente = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=False
    ).count()
    
    if propositions_en_attente > 0:
        print(f"   Propositions en attente: {propositions_en_attente}")

print("\n" + "=" * 80)
print("RÉSUMÉ")
print("=" * 80)

enseignants_avec_cours = 0
enseignants_sans_cours = 0

for enseignant in enseignants:
    cours_count = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().count()
    
    if cours_count > 0:
        enseignants_avec_cours += 1
    else:
        enseignants_sans_cours += 1

print(f"Total enseignants: {enseignants.count()}")
print(f"Enseignants avec cours: {enseignants_avec_cours}")
print(f"Enseignants sans cours: {enseignants_sans_cours}")
print("=" * 80)