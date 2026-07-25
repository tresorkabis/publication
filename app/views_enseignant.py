from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Personnel, Cours, Evaluation, ProposalCoursEnseignant, Filiere

@login_required
def compte_enseignant(request, personnel_id):
    """Affiche le compte détaillé d'un enseignant"""
    enseignant = get_object_or_404(Personnel, pk=personnel_id)
    user = enseignant.user
    
    # Récupérer les cours assignés à l'enseignant
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().select_related('filiere', 'semestre', 'annee_etude')
    
    # Récupérer les évaluations liées aux cours de l'enseignant
    evaluations = Evaluation.objects.filter(
        cours__in=cours_assignes
    ).select_related('cours', 'type_evaluation', 'cours__filiere').order_by('-date')
    
    # Statistiques
    total_cours = cours_assignes.count()
    total_evaluations = evaluations.count()
    total_evaluations_publiees = evaluations.filter(is_published=True).count()
    total_evaluations_en_attente = evaluations.filter(is_published=False).count()
    
    # Récupérer les filières enseignées
    filieres_enseignees = Filiere.objects.filter(
        cours__in=cours_assignes
    ).distinct()
    
    # Récupérer les propositions de cours (en attente et acceptées)
    propositions_en_attente = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=False
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')
    
    propositions_acceptees = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=True
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')
    
    context = {
        'enseignant': enseignant,
        'user': user,
        'cours_assignes': cours_assignes,
        'evaluations': evaluations[:10],  # Les 10 dernières évaluations
        'total_cours': total_cours,
        'total_evaluations': total_evaluations,
        'total_evaluations_publiees': total_evaluations_publiees,
        'total_evaluations_en_attente': total_evaluations_en_attente,
        'filieres_enseignees': filieres_enseignees,
        'propositions_en_attente': propositions_en_attente,
        'propositions_acceptees': propositions_acceptees,
    }
    
    return render(request, 'dashboard/compte_enseignant.html', context)