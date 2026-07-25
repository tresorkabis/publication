#!/usr/bin/env python
"""
Script pour vérifier les enseignants et leurs cours assignés
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from app.models import *

# Rediriger la sortie vers un fichier
output = open('resultats_enseignants.txt', 'w', encoding='utf-8')

output.write("=" * 80 + "\n")
output.write("LISTE DES ENSEIGNANTS ET LEURS COURS ASSIGNÉS\n")
output.write("=" * 80 + "\n")

enseignants = Personnel.objects.select_related('user').all()

enseignants_avec_cours = []
enseignants_sans_cours = []

for enseignant in enseignants:
    user = enseignant.user
    output.write(f"\n📚 Enseignant: {user.get_full_name()}\n")
    output.write(f"   Username: {user.username}\n")
    output.write(f"   Email: {user.email}\n")
    output.write(f"   Fonction: {enseignant.fonction.intitule if enseignant.fonction else 'N/A'}\n")
    output.write(f"   Grade: {enseignant.grade}\n")
    
    # Récupérer les cours assignés (propositions acceptées)
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().select_related('filiere', 'semestre')
    
    if cours_assignes:
        output.write(f"   Cours assignés ({cours_assignes.count()}):\n")
        for cours in cours_assignes:
            output.write(f"      - {cours.libelle} ({cours.code}) - {cours.filiere.libelle} - {cours.semestre.libelle}\n")
        enseignants_avec_cours.append(enseignant)
    else:
        output.write(f"   Cours assignés: Aucun\n")
        enseignants_sans_cours.append(enseignant)
    
    # Vérifier les propositions en attente
    propositions_en_attente = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=False
    ).count()
    
    if propositions_en_attente > 0:
        output.write(f"   Propositions en attente: {propositions_en_attente}\n")

output.write("\n" + "=" * 80 + "\n")
output.write("RÉSUMÉ\n")
output.write("=" * 80 + "\n")

output.write(f"Total enseignants: {enseignants.count()}\n")
output.write(f"Enseignants avec cours: {len(enseignants_avec_cours)}\n")
output.write(f"Enseignants sans cours: {len(enseignants_sans_cours)}\n")

output.write("\n" + "=" * 80 + "\n")
output.write("ENSEIGNANTS AVEC COURS ASSIGNÉS:\n")
output.write("=" * 80 + "\n")

for enseignant in enseignants_avec_cours:
    user = enseignant.user
    output.write(f"✓ {user.get_full_name()} ({user.username})\n")

output.write("\n" + "=" * 80 + "\n")
output.write("ENSEIGNANTS SANS COURS:\n")
output.write("=" * 80 + "\n")

for enseignant in enseignants_sans_cours:
    user = enseignant.user
    output.write(f"✗ {user.get_full_name()} ({user.username})\n")

output.write("\n" + "=" * 80 + "\n")
output.write("COMPTE D'UN ENSEIGNANT AVEC DES COURS:\n")
output.write("=" * 80 + "\n")

if enseignants_avec_cours:
    enseignant_exemple = enseignants_avec_cours[0]
    user = enseignant_exemple.user
    output.write(f"Username: {user.username}\n")
    output.write(f"Nom complet: {user.get_full_name()}\n")
    output.write(f"Email: {user.email}\n")
    output.write(f"Mot de passe par défaut: demo\n")
    output.write(f"\nPour se connecter: http://localhost:8000/connexion/\n")

output.close()

print("Résultats enregistrés dans resultats_enseignants.txt")
print(f"Enseignants avec cours: {len(enseignants_avec_cours)}")
print(f"Enseignants sans cours: {len(enseignants_sans_cours)}")

if enseignants_avec_cours:
    user = enseignants_avec_cours[0].user
    print(f"\nCompte d'un enseignant avec cours:")
    print(f"  Username: {user.username}")
    print(f"  Nom: {user.get_full_name()}")
    print(f"  Email: {user.email}")
    print(f"  Mot de passe: demo")
