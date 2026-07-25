from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from app.models import Etudiant, Personnel, Role, UtilisateurRole

User = get_user_model()

@login_required
def comptes_demo(request):
    """Affiche tous les comptes de démonstration"""
    
    # Récupérer tous les utilisateurs avec leurs rôles
    utilisateurs = User.objects.all().select_related('personnel', 'etudiant').prefetch_related('utilisateur_roles__role')
    
    # Organiser les données par type d'utilisateur
    comptes = []
    for user in utilisateurs:
        roles = user.role_labels
        
        # Déterminer le type de compte
        if 'etudiant' in roles:
            type_compte = 'Étudiant'
            try:
                etudiant = user.etudiant
                matricule = etudiant.matricule
                filiere = etudiant.inscriptions.first().promotion.filiere.libelle if etudiant.inscriptions.exists() else '-'
                promotion = etudiant.inscriptions.first().promotion.libelle if etudiant.inscriptions.exists() else '-'
            except:
                matricule = '-'
                filiere = '-'
                promotion = '-'
        elif 'enseignant' in roles or 'chef de filière' in roles:
            type_compte = 'Enseignant'
            try:
                personnel = user.personnel
                matricule = user.mat
                filiere = '-'
                promotion = '-'
            except:
                matricule = '-'
                filiere = '-'
                promotion = '-'
        elif 'president' in roles:
            type_compte = 'Président'
            matricule = user.mat
            filiere = '-'
            promotion = '-'
        else:
            type_compte = 'Autre'
            matricule = user.mat
            filiere = '-'
            promotion = '-'
        
        comptes.append({
            'user': user,
            'type_compte': type_compte,
            'roles': roles,
            'matricule': matricule,
            'filiere': filiere,
            'promotion': promotion,
            'email': user.email,
            'is_active': user.is_active,
            'is_validated': user.is_validated,
        })
    
    # Statistiques
    total_etudiants = sum(1 for c in comptes if c['type_compte'] == 'Étudiant')
    total_enseignants = sum(1 for c in comptes if c['type_compte'] == 'Enseignant')
    total_presidents = sum(1 for c in comptes if c['type_compte'] == 'Président')
    total_utilisateurs = len(comptes)
    
    context = {
        'comptes': comptes,
        'total_utilisateurs': total_utilisateurs,
        'total_etudiants': total_etudiants,
        'total_enseignants': total_enseignants,
        'total_presidents': total_presidents,
    }
    
    return render(request, 'dashboard/comptes_demo.html', context)