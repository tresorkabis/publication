import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import Count, Q, F, Avg, Max, Min
from .models import *
from .forms import UserRegistrationForm, UserProfileForm, PlanificationExamenForm, PropositionCoursForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone

def home(request):
    from django.db.models import Count
    context = {
        'total_students': Etudiant.objects.count(),
        'total_filieres': Filiere.objects.count(),
        'total_evaluations': Evaluation.objects.count(),
        'total_cotations': Cotation.objects.count(),
        'filieres': Filiere.objects.annotate(
            total_promotions=Count('promotion'),
            total_cours=Count('cours')
        ).all(),
        'recent_evaluations': Evaluation.objects.select_related('cours', 'type_evaluation').order_by('-id')[:5],
    }
    return render(request, 'home.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_validated = False
            user.save()
            Etudiant.objects.get_or_create(user=user)
            role_etudiant, _ = Role.objects.get_or_create(libelle='etudiant')
            UtilisateurRole.objects.get_or_create(user=user, role=role_etudiant)
            messages.success(request, "Inscription enregistrée. Votre compte doit être validé par le secrétariat avant activation.")
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})

@login_required
def dashboard(request):
    # Rediriger les enseignants vers leur dashboard spécifique (sauf les administrateurs)
    if not (request.user.is_superuser or request.user.is_staff) and request.user.has_role('enseignant') and hasattr(request.user, 'personnel'):
        return redirect('dashboard_enseignant')
    
    if hasattr(request.user, 'etudiant'):
        student = request.user.etudiant
        cotations_qs = (
            Cotation.objects.filter(etudiant=student, evaluation__is_published=True)
            .select_related('evaluation', 'evaluation__cours', 'evaluation__type_evaluation')
            .order_by('-evaluation__date', '-id')
        )

        # Regrouper les cotations par cours avec annotations optimisées
        cours_notes = {}
        for c in cotations_qs:
            cours_id = c.evaluation.cours.id
            if cours_id not in cours_notes:
                cours_notes[cours_id] = {
                    'cours': c.evaluation.cours,
                    'cotations': [],
                    'total_pondere': 0,
                    'total_coeffs': 0,
                    'moyenne': None,
                    'notes_publiees': [],
                }
            
            status = 'reussite' if c.note >= 10 else 'echec'
            cours_notes[cours_id]['cotations'].append({
                'cotation': c,
                'status': status,
                'type_evaluation': c.evaluation.type_evaluation.libelle,
                'date': c.evaluation.date,
                'is_published': c.evaluation.is_published,
            })
            
            # Calcul pour la moyenne pondérée (uniquement pour les notes publiées)
            if c.evaluation.is_published:
                coeff = c.evaluation.coefficient
                note_float = float(c.note)
                cours_notes[cours_id]['total_pondere'] += note_float * coeff
                cours_notes[cours_id]['total_coeffs'] += coeff
                cours_notes[cours_id]['notes_publiees'].append(note_float)

        # Calculer la moyenne finale pour chaque cours
        moyennes_globales = []
        for data in cours_notes.values():
            if data['total_coeffs'] > 0:
                moyenne_cours = data['total_pondere'] / data['total_coeffs']
                data['moyenne'] = round(moyenne_cours, 2)
                moyennes_globales.append(moyenne_cours)
        
        # Calcul de la moyenne générale de l'étudiant sur tous les cours
        moyenne_generale = round(sum(moyennes_globales) / len(moyennes_globales), 2) if moyennes_globales else None
        
        # Calculer les statistiques
        total_evaluations = len(cotations_qs)
        evaluations_publiees = sum(1 for c in cotations_qs if c.evaluation.is_published)
        moyenne_meilleur_cours = max(moyennes_globales) if moyennes_globales else None
        moyenne_pire_cours = min(moyennes_globales) if moyennes_globales else None

        context = {
            'student': student,
            'cours_notes': list(cours_notes.values()),
            'student_average': moyenne_generale,
            'total_evaluations': total_evaluations,
            'evaluations_publiees': evaluations_publiees,
            'moyenne_meilleur_cours': moyenne_meilleur_cours,
            'moyenne_pire_cours': moyenne_pire_cours,
            'is_student': True,
        }
        return render(request, 'dashboard.html', context)

    # Périodes d'examens actives pour toutes les filières (affichage global)
    toutes_periodes_examens = CalendrierAcademique.objects.filter(
        est_actif=True
    ).select_related('filiere', 'promotion', 'annee_etude', 'semestre').order_by('date_debut')

    if request.user.has_role('chef de filière'):
        chef_personnel = getattr(request.user, 'personnel', None)
        raw_chef_filieres = Filiere.objects.filter(chef=chef_personnel).order_by('libelle', 'code') if chef_personnel else Filiere.objects.none()
        chef_filieres = []
        seen_filiere_labels = set()
        for filiere in raw_chef_filieres:
            if filiere.libelle in seen_filiere_labels:
                continue
            seen_filiere_labels.add(filiere.libelle)
            chef_filieres.append(filiere)

        chef_evaluations = Evaluation.objects.filter(cours__filiere__in=chef_filieres).select_related('cours', 'type_evaluation').order_by('-date', '-id')
        
        # Périodes d'examens pour les filières du chef
        chef_periodes_examens = toutes_periodes_examens.filter(filiere__in=chef_filieres)
        
        context = {
            'is_student': False,
            'is_chef_filiere': True,
            'chef_personnel': chef_personnel,
            'chef_filieres': chef_filieres,
            'chef_students_count': Etudiant.objects.filter(inscriptions__promotion__filiere__in=chef_filieres).distinct().count(),
            'chef_courses_count': Cours.objects.filter(filiere__in=chef_filieres).count(),
            'chef_evaluations_count': chef_evaluations.count(),
            'chef_published_evaluations_count': chef_evaluations.filter(is_published=True).count(),
            'chef_pending_evaluations': chef_evaluations.filter(is_published=False)[:5],
            'chef_promotions': Promotion.objects.filter(filiere__in=chef_filieres).distinct(),
            'periodes_examens': chef_periodes_examens,
        }
        return render(request, 'dashboard.html', context)

    if request.user.has_role('president'):
        # Le dashboard du président est la page de validation des notes par promotion.
        # On utilise la vue `liste_evaluations_a_valider` comme dashboard principal
        # mais on ne redirige pas pour lui permettre d'accéder aux autres menus si besoin.
        return liste_evaluations_a_valider(request)


    # Statistiques générales
    total_users = User.objects.count()
    total_students = Etudiant.objects.count()
    total_staff = Personnel.objects.count()
    total_filieres = Filiere.objects.count()
    total_evaluations = Evaluation.objects.count()
    total_published_evaluations = Evaluation.objects.filter(is_published=True).count()
    pending_validations_count = User.objects.filter(is_active=False, is_validated=False).count()

    # Données pour le graphique des étudiants par promotion
    promotions_data = list(Promotion.objects.values_list('libelle', flat=True))
    students_count_data = []
    for promotion in Promotion.objects.all():
        students_count_data.append(Inscription.objects.filter(promotion=promotion).count())

    # Dernières inscriptions (5 dernières)
    recent_inscriptions = Inscription.objects.select_related('etudiant__user', 'promotion').order_by('-id')[:5]

    # Dernières évaluations (5 dernières)
    recent_evaluations = Evaluation.objects.select_related('cours', 'type_evaluation').order_by('-date')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_filieres': total_filieres,
        'total_evaluations': total_evaluations,
        'total_published_evaluations': total_published_evaluations,
        'pending_validations_count': pending_validations_count,
        'promotions_data': json.dumps(promotions_data),
        'students_count_data': json.dumps(students_count_data),
        'recent_inscriptions': recent_inscriptions,
        'recent_evaluations': recent_evaluations,
        'is_student': False,
    }

    return render(request, 'dashboard.html', context)

@login_required
def pending_validations(request):
    if not (request.user.is_staff or request.user.has_role('president')):
        return redirect('dashboard')
    users = User.objects.filter(is_active=False, is_validated=False).order_by('date_joined')
    return render(request, 'pending_validations.html', {'users': users})

@login_required
def validate_user(request, user_id):
    if not (request.user.is_staff or request.user.has_role('president')):
        return redirect('dashboard')
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user.is_validated = True
        user.is_active = True
        user.save()
        messages.success(request, f"Le compte de {user.username} a été validé.")
    return redirect('pending_validations')


def results_list(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if hasattr(request.user, 'etudiant'):
        cotations = Cotation.objects.filter(
            etudiant=request.user.etudiant
        ).select_related('evaluation', 'evaluation__cours')
        return render(request, 'results/student_results.html', {'cotations': cotations})

    return redirect('dashboard')

@login_required
def enter_marks(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') or request.user.has_role('chef de filière')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')

    evaluation = Evaluation.objects.get(pk=evaluation_id)
    students = Etudiant.objects.filter(inscription__promotion__filiere=evaluation.cours.filiere).distinct()

    if request.method == 'POST':
        for student in students:
            note = request.POST.get(f'note_{student.pk}')
            if note:
                Cotation.objects.update_or_create(
                    etudiant=student,
                    evaluation=evaluation,
                    defaults={'note': note}
                )
        messages.success(request, "Les notes ont été enregistrées avec succès.")
        return redirect('dashboard')

    return render(request, 'results/enter_marks.html', {'evaluation': evaluation, 'students': students})

@login_required
def upload_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, "Votre photo de profil a été mise à jour.")
    return redirect('dashboard')

@login_required
def print_results(request):
    if hasattr(request.user, 'etudiant'):
        cotations = Cotation.objects.filter(
            etudiant=request.user.etudiant,
            evaluation__is_published=True
        ).select_related('evaluation', 'evaluation__cours', 'evaluation__type_evaluation')
        return render(request, 'results/print_results.html', {'cotations': cotations, 'today': timezone.now()})
    return redirect('dashboard')

@login_required
def edit_mark(request, cotation_id):
    if not (hasattr(request.user, 'personnel') or request.user.has_role('chef de filière')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')

    cotation = Cotation.objects.get(pk=cotation_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        if note:
            cotation.note = note
            cotation.save()
            messages.success(request, "La note a été modifiée.")
            return redirect('manage_marks', evaluation_id=cotation.evaluation.id)

    return render(request, 'results/edit_mark.html', {'cotation': cotation})

@login_required
def delete_mark(request, cotation_id):
    if not (hasattr(request.user, 'personnel') or request.user.has_role('chef de filière')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')

    cotation = Cotation.objects.get(pk=cotation_id)
    eval_id = cotation.evaluation.id
    cotation.delete()
    messages.success(request, "La note a été supprimée.")
    return redirect('manage_marks', evaluation_id=eval_id)

@login_required
def planifier_examen(request):
    if not request.user.has_role('chef de filière'):
        messages.error(request, "Accès réservé au chef de filière.")
        return redirect('dashboard')

    chef_personnel = getattr(request.user, 'personnel', None)
    filieres = Filiere.objects.filter(chef=chef_personnel).order_by('libelle', 'code') if chef_personnel else Filiere.objects.none()
    promotions = Promotion.objects.filter(filiere__in=filieres).distinct() if filieres else Promotion.objects.none()

    # Examens déjà planifiés pour les filières du chef
    examens_planifies = Evaluation.objects.filter(
        cours__filiere__in=filieres
    ).select_related(
        'cours', 'type_evaluation', 'calendrier'
    ).order_by('-date', '-id')

    # Calendriers académiques actifs pour les filières du chef
    calendriers = CalendrierAcademique.objects.filter(
        filiere__in=filieres,
        est_actif=True
    ).select_related('promotion', 'semestre', 'annee_etude').order_by('annee_etude__ordre', 'date_debut')

    # Grouper les calendriers par année d'étude
    calendriers_groupes = {}
    for cal in calendriers:
        annee_label = cal.annee_etude.libelle if cal.annee_etude else "Tronc commun"
        if annee_label not in calendriers_groupes:
            calendriers_groupes[annee_label] = []
        calendriers_groupes[annee_label].append(cal)

    if request.method == 'POST':
        form = PlanificationExamenForm(request.POST, filieres=filieres)
        if form.is_valid():
            evaluation = form.save()
            messages.success(request, "L'examen a été planifié avec succès.")
            return redirect('planifier_examen')
    else:
        form = PlanificationExamenForm(filieres=filieres)

    return render(request, 'results/planifier_examen.html', {
        'form': form,
        'filieres': filieres,
        'promotions': promotions,
        'examens_planifies': examens_planifies,
        'calendriers': calendriers,
        'calendriers_groupes': calendriers_groupes,
        'periodes_examens': calendriers,
        'today': timezone.now().date(),
    })

@login_required
def dashboard_enseignant(request):
    if not (request.user.is_superuser or request.user.is_staff or (hasattr(request.user, 'personnel') and request.user.has_role('enseignant'))):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    
    # Cours assignés à l'enseignant
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant, 
        propositions_enseignants__est_accepte=True
    ).distinct().select_related(
        'filiere', 'semestre', 'annee_etude'
    ).annotate(
        nb_etudiants=Count('filiere__promotion__inscriptions__etudiant', distinct=True, filter=Q(
            filiere__promotion__libelle__icontains=F('annee_etude__code')))
    )
    
    # Évaluations à venir pour les cours de l'enseignant
    evaluations_a_venir = Evaluation.objects.filter(
        cours__in=cours_assignes,
        is_published=False
    ).select_related('cours', 'type_evaluation').order_by('date')[:10]
    
    # Évaluations publiées récemment
    evaluations_publiees = Evaluation.objects.filter(
        cours__in=cours_assignes,
        is_published=True
    ).select_related('cours', 'type_evaluation').order_by('-published_at')[:10]
    
    # Propositions de cours en attente
    propositions_en_attente = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=False
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')[:5]
    
    # Propositions acceptées
    propositions_acceptees = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=True
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')[:5]
    
    context = {
        'is_enseignant': True,
        'enseignant': enseignant,
        'cours_assignes': cours_assignes,
        'cours_count': cours_assignes.count(),
        'evaluations_a_venir': evaluations_a_venir,
        'evaluations_publiees': evaluations_publiees,
        'propositions_en_attente': propositions_en_attente,
        'propositions_acceptees': propositions_acceptees,
    }
    
    return render(request, 'dashboard/dashboard_enseignant.html', context)

@login_required
def evaluations_enseignant(request):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    
    # Récupérer les cours assignés à l'enseignant
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct()
    
    # Récupérer toutes les évaluations pour les cours de l'enseignant
    evaluations = Evaluation.objects.filter(
        cours__in=cours_assignes
    ).select_related(
        'cours', 'cours__filiere', 'cours__semestre', 'cours__annee_etude', 'type_evaluation'
    ).order_by('-date', '-id')
    
    # Filtre
    filtre = request.GET.get('filtre', 'toutes')
    if filtre == 'a_venir':
        evaluations = evaluations.filter(is_published=False)
    elif filtre == 'publiees':
        evaluations = evaluations.filter(is_published=True)
    
    # Compter les totaux avant d'ajouter les attributs
    total_evaluations = evaluations.count()
    evaluations_a_venir_count = evaluations.filter(is_published=False).count()
    evaluations_publiees_count = evaluations.filter(is_published=True).count()
    
    # Ajouter le nombre d'étudiants et statistiques de notes pour chaque évaluation
    from django.db.models import Count, Avg, Subquery, OuterRef
    
    # Utiliser les annotations pour éviter les boucles et les requêtes N+1
    evaluations = evaluations.annotate(
        nb_etudiants=Count('cotations__etudiant', distinct=True),
        nb_notes_saisies=Count('cotations__note'),
        moyenne=Avg('cotations__note')
    )
    
    # La conversion en liste est toujours utile si vous devez faire d'autres manipulations en Python
    evaluations_list = list(evaluations)
    
    context = {
        'evaluations': evaluations_list,
        'total_evaluations': total_evaluations,
        'evaluations_a_venir_count': evaluations_a_venir_count,
        'evaluations_publiees_count': evaluations_publiees_count,
        'filtre': filtre,
        'enseignant': enseignant,
    }
    
    return render(request, 'dashboard/evaluations_enseignant.html', context)


@login_required
def propositions_enseignant(request):
    """Affiche toutes les propositions de cours de l'enseignant"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel

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
        'propositions_en_attente': propositions_en_attente,
        'propositions_acceptees': propositions_acceptees,
    }

    return render(request, 'dashboard/propositions_enseignant.html', context)


@login_required
def cours_enseignant(request):
    if not hasattr(request.user, 'personnel'):
        messages.error(request, "Accès réservé au personnel.")
        return redirect('dashboard')
    
    if not request.user.has_role('enseignant'):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    
    # Récupérer les cours assignés à l'enseignant
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().select_related('filiere', 'semestre', 'annee_etude')
    
    # Pour chaque cours, récupérer les évaluations associées
    cours_avec_evaluations = []
    for cours in cours_assignes:
        evaluations = Evaluation.objects.filter(cours=cours).select_related('type_evaluation').order_by('-date')
        cours_avec_evaluations.append({
            'cours': cours,
            'evaluations': evaluations,
            'evaluations_count': evaluations.count(),
            'evaluations_publiees': evaluations.filter(is_published=True).count(),
        })
    
    context = {
        'cours_avec_evaluations': cours_avec_evaluations,
        'enseignant': enseignant,
    }
    
    return render(request, 'dashboard/cours_enseignant.html', context)


@login_required
def creer_evaluation_enseignant(request, cours_id):
    """Permet à un enseignant de créer une évaluation pour un de ses cours"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    cours = get_object_or_404(Cours, pk=cours_id)

    # Vérifier que l'enseignant est bien assigné à ce cours
    is_assigned = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        cours=cours,
        est_accepte=True
    ).exists()

    if not is_assigned:
        messages.error(request, "Vous n'êtes pas autorisé à créer une évaluation pour ce cours.")
        return redirect('cours_enseignant')

    if request.method == 'POST':
        type_eval_id = request.POST.get('type_evaluation')
        date_eval = request.POST.get('date')
        coefficient = request.POST.get('coefficient', 1)
        duree = request.POST.get('duree_minutes', 60)

        if not type_eval_id or not date_eval:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        else:
            type_eval = get_object_or_404(TypeEvaluation, pk=type_eval_id)
            evaluation = Evaluation.objects.create(
                type_evaluation=type_eval,
                cours=cours,
                date=date_eval,
                coefficient=coefficient,
                duree_minutes=duree,
                is_published=False
            )
            messages.success(request, f"Évaluation '{type_eval.libelle}' créée avec succès pour le cours '{cours.libelle}'.")
            return redirect('saisie_notes_enseignant', evaluation_id=evaluation.pk)

    types_eval = TypeEvaluation.objects.all()
    return render(request, 'dashboard/creer_evaluation_enseignant.html', {
        'cours': cours,
        'types_evaluation': types_eval,
        'enseignant': enseignant,
    })

@login_required
def fiche_de_cotes_cours(request, cours_id):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    cours = get_object_or_404(Cours, pk=cours_id)

    # Sécurité : Vérifier que l'enseignant est bien assigné à ce cours
    is_assigned = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        cours=cours,
        est_accepte=True
    ).exists()

    if not is_assigned:
        messages.error(request, "Vous n'êtes pas autorisé à consulter cette fiche de cotes.")
        return redirect('cours_enseignant')

    # Récupérer les étudiants inscrits à la bonne année d'étude
    students = Etudiant.objects.filter(
        inscriptions__promotion__filiere=cours.filiere,
        inscriptions__promotion__libelle__icontains=cours.annee_etude.code
    ).distinct().select_related('user').order_by('user__nom', 'user__postnom', 'user__prenom')

    # Récupérer toutes les évaluations et cotations pour ce cours
    evaluations = Evaluation.objects.filter(cours=cours).select_related('type_evaluation')
    cotations = Cotation.objects.filter(evaluation__in=evaluations).select_related('evaluation', 'evaluation__type_evaluation')

    # Organiser les données pour la fiche de cotes
    fiche_de_cotes = []
    for student in students:
        student_data = {
            'etudiant': student,
            'notes': {}, # ex: {'Examen': 15, 'Interrogation': 12}
            'total_pondere': 0,
            'total_coeffs': 0,
            'moyenne': None
        }

        # Regrouper les notes par type d'évaluation
        for cotation in cotations.filter(etudiant=student):
            type_eval = cotation.evaluation.type_evaluation.libelle
            note_value = float(cotation.note)

            # Ramener la note sur le barème correspondant (Travail Pratique sur 5, Interrogation sur 5, Examen sur 10)
            if type_eval == 'Travail Pratique':
                note_value = round(note_value / 4, 1)  # Convertir de /20 à /5
            elif type_eval == 'Interrogation':
                note_value = round(note_value / 4, 1)  # Convertir de /20 à /5
            elif type_eval == 'Examen':
                note_value = round(note_value / 2, 1)  # Convertir de /20 à /10

            student_data['notes'][type_eval] = note_value

        # Calculer la moyenne = somme des notes sur la ligne
        somme_notes = 0
        for type_eval in ['Travail Pratique', 'Interrogation', 'Examen']:
            note = student_data['notes'].get(type_eval)
            if note is not None:
                somme_notes += note
        student_data['moyenne'] = round(somme_notes)

        fiche_de_cotes.append(student_data)

    # Extraire les types d'évaluations pour les colonnes du tableau
    types_evaluations = list(evaluations.values_list('type_evaluation__libelle', flat=True).distinct())

    # Ordre personnalisé : Travail Pratique, Interrogation, Examen
    ordre_types = {'Travail Pratique': 1, 'Interrogation': 2, 'Examen': 3}
    types_evaluations.sort(key=lambda t: ordre_types.get(t, 99))

    # Notes maximales par type d'évaluation
    notes_max = {'Travail Pratique': 5, 'Interrogation': 5, 'Examen': 10}


    context = {
        'cours': cours,
        'fiche_de_cotes': fiche_de_cotes,
        'types_evaluations': types_evaluations,
        'notes_max': notes_max,
    }
    return render(request, 'dashboard/fiche_de_cotes.html', context)

@login_required
def profil_enseignant(request):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    
    # Cours assignés
    cours_assignes = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).distinct().select_related('filiere', 'semestre', 'annee_etude')
    
    # Évaluations
    evaluations_a_venir = Evaluation.objects.filter(
        cours__in=cours_assignes,
        is_published=False
    ).select_related('cours', 'type_evaluation').order_by('date')[:10]
    
    evaluations_publiees = Evaluation.objects.filter(
        cours__in=cours_assignes,
        is_published=True
    ).select_related('cours', 'type_evaluation').order_by('-published_at')[:10]
    
    # Propositions
    propositions_en_attente = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=False
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')[:5]
    
    propositions_acceptees = ProposalCoursEnseignant.objects.filter(
        enseignant=enseignant,
        est_accepte=True
    ).select_related('cours', 'cours__filiere').order_by('-date_proposition')[:5]
    
    context = {
        'enseignant': enseignant,
        'cours_assignes': cours_assignes,
        'cours_count': cours_assignes.count(),
        'evaluations_a_venir': evaluations_a_venir,
        'evaluations_publiees': evaluations_publiees,
        'propositions_en_attente': propositions_en_attente,
        'propositions_acceptees': propositions_acceptees,
    }
    
    return render(request, 'dashboard/profil_enseignant.html', context)

@login_required
def saisie_notes_enseignant(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    evaluation = get_object_or_404(Evaluation, pk=evaluation_id)
    
    # Vérifier que l'enseignant est bien assigné à ce cours
    cours_enseignant = Cours.objects.filter(
        propositions_enseignants__enseignant=enseignant,
        propositions_enseignants__est_accepte=True
    ).filter(pk=evaluation.cours.pk).exists()
    
    if not cours_enseignant:
        messages.error(request, "Vous n'êtes pas autorisé à saisir des notes pour cette évaluation.")
        return redirect('dashboard_enseignant')
    
    # Récupérer tous les étudiants inscrits dans la filière du cours
    students = Etudiant.objects.filter(
        inscriptions__promotion__filiere=evaluation.cours.filiere
    ).distinct().select_related('user').order_by('user__nom', 'user__postnom', 'user__prenom')
    
    if request.method == 'POST':
        from decimal import Decimal, InvalidOperation
        notes_saved = 0
        erreurs = []
        
        for student in students:
            note_key = f'note_{student.pk}'
            note = request.POST.get(note_key)
            
            if note is not None and note.strip() != '':
                note = note.replace(',', '.').strip()
                try:
                    note_decimal = Decimal(note)
                    if note_decimal < 0 or note_decimal > 20:
                        erreurs.append(f"Note invalide pour {student.user.get_full_name()} : {note} (doit être entre 0 et 20)")
                        continue
                    cotation, created = Cotation.objects.update_or_create(
                        etudiant=student,
                        evaluation=evaluation,
                        defaults={'note': note_decimal}
                    )
                    notes_saved += 1
                except (InvalidOperation, ValueError):
                    erreurs.append(f"Format invalide pour {student.user.get_full_name()} : {note}")
        
        # Ne pas rediriger, rester sur la page pour permettre la révision
        if notes_saved > 0:
            messages.success(request, f"✅ {notes_saved} note(s) enregistrée(s) avec succès. Vous pouvez réviser et modifier ci-dessous.")
        else:
            messages.warning(request, "Aucune note à enregistrer. Veuillez saisir des notes.")
        
        if erreurs:
            for erreur in erreurs:
                messages.error(request, erreur)
    else:
        # GET request: S'assurer que chaque étudiant a une cotation, même avec 0
        # pour que le template puisse afficher une valeur par défaut.
        for student in students:
            Cotation.objects.get_or_create(
                etudiant=student,
                evaluation=evaluation,
                defaults={'note': 0}
            )
    
    # Récupérer les notes existantes - Utiliser etudiant_id directement
    cotations = Cotation.objects.filter(evaluation=evaluation)
    notes_map = {}
    for c in cotations:
        notes_map[c.etudiant_id] = c.note
    
    # Préparer les données pour le template
    students_notes = []
    for student in students:
        note = notes_map.get(student.pk)
        status = None
        if note is not None:
            if note >= 10:
                status = 'reussite'
            else:
                status = 'echec'
        students_notes.append({
            'student': student,
            'note': note,
            'status': status,
        })
    
    context = {
        'evaluation': evaluation,
        'students_notes': students_notes,
        'enseignant': enseignant,
    }
    
    return render(request, 'dashboard/saisie_notes_enseignant.html', context)

@login_required
def proposer_cours(request):
    if not request.user.has_role('chef de filière'):
        messages.error(request, "Accès réservé au chef de filière.")
        return redirect('dashboard')

    chef_personnel = getattr(request.user, 'personnel', None)
    filieres = Filiere.objects.filter(chef=chef_personnel).order_by('libelle', 'code') if chef_personnel else Filiere.objects.none()

    if request.method == 'POST':
        form = PropositionCoursForm(request.POST, filieres=filieres)
        if form.is_valid():
            form.save()
            messages.success(request, "La proposition de cours a été enregistrée.")
            return redirect('proposer_cours')
    else:
        form = PropositionCoursForm(filieres=filieres)

    return render(request, 'results/proposer_cours.html', {'form': form, 'filieres': filieres})


@login_required
def accepter_proposition(request, proposition_id):
    """Permet à un enseignant d'accepter une proposition de cours"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('enseignant')):
        messages.error(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    enseignant = request.user.personnel
    proposition = get_object_or_404(ProposalCoursEnseignant, pk=proposition_id, enseignant=enseignant)

    if request.method == 'POST':
        proposition.est_accepte = True
        proposition.save()
        messages.success(request, f"Proposition acceptée ! Le cours '{proposition.cours.libelle}' a été ajouté à vos cours.")
        return redirect('dashboard_enseignant')

    return redirect('dashboard_enseignant')

@login_required
def manage_marks(request, evaluation_id):
    if not (request.user.has_role('chef de filière') or request.user.has_role('president')):
        messages.error(request, "Accès réservé au chef de filière ou au président.")
        return redirect('dashboard')

    evaluation = Evaluation.objects.get(pk=evaluation_id)
    cotations = Cotation.objects.filter(evaluation=evaluation).select_related('etudiant', 'etudiant__user')
    students = (
        Etudiant.objects.filter(inscriptions__promotion__filiere=evaluation.cours.filiere)
        .distinct()
        .select_related('user')
        .order_by('user__nom', 'user__postnom', 'user__prenom')
    )
    promotions = (
        Promotion.objects.filter(inscriptions__etudiant__in=students)
        .distinct()
        .order_by('libelle')
    )
    primary_promotion = promotions.first()
    cotation_map = {cotation.etudiant_id: cotation for cotation in cotations}
    student_entries = [
        {
            'student': student,
            'cotation': cotation_map.get(student.id),
        }
        for student in students
    ]

    return render(request, 'results/manage_marks.html', {
        'evaluation': evaluation,
        'student_entries': student_entries,
        'promotion': primary_promotion,
        'filiere': evaluation.cours.filiere,
    })

@login_required
def publish_evaluation(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    president_personnel = request.user.personnel
    evaluation = get_object_or_404(Evaluation, pk=evaluation_id)

    if request.method == 'POST':
        if not Cotation.objects.filter(evaluation=evaluation).exists():
            messages.error(request, "Aucune note n'a été saisie pour cette évaluation.")
            return redirect('manage_marks', evaluation_id=evaluation_id)

        evaluation.is_published = True
        evaluation.published_at = timezone.now()
        evaluation.save()
        messages.success(request, "L'évaluation a été validée et publiée.")
        return redirect('manage_marks', evaluation_id=evaluation_id)

    return render(request, 'results/publish_evaluation.html', {'evaluation': evaluation})


@login_required
def valider_moyenne_etudiant(request, etudiant_id):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    etudiant = get_object_or_404(Etudiant, pk=etudiant_id)

    if request.method == 'POST':
        # Ici on pourrait ajouter une logique métier, ex: stocker une validation explicitement
        # Pour l'instant, on redirme simple avec un message.
        messages.success(request, f"La moyenne de {etudiant.user.get_full_name()} a été validée.")
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def liste_evaluations_a_valider(request):
    """Liste des filières avec leurs promotions ayant des notes en attente de validation"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    # Récupérer toutes les filières avec leurs promotions
    filieres = Filiere.objects.all().order_by('libelle')
    
    filieres_data = []
    total_en_attente = 0
    
    for filiere in filieres:
        # Récupérer toutes les promotions de cette filière
        promotions = Promotion.objects.filter(
            filiere=filiere
        ).annotate(
            nb_evaluations_attente=Count(
                'filiere__cours__evaluation',
                filter=Q(
                    filiere__cours__evaluation__is_published=False,
                    filiere__cours__evaluation__cotations__isnull=False
                ),
                distinct=True
            ),
            nb_evaluations_validees=Count(
                'filiere__cours__evaluation',
                filter=Q(
                    filiere__cours__evaluation__is_published=True
                ),
                distinct=True
            ),
            nb_etudiants=Count('inscriptions__etudiant', distinct=True)
        ).order_by('libelle')
        
        if promotions.exists():
            total_en_attente += sum(p.nb_evaluations_attente for p in promotions)
            filieres_data.append({
                'filiere': filiere,
                'promotions': promotions,
            })

    context = {
        'filieres_data': filieres_data,
        'total_en_attente': total_en_attente,
    }
    return render(request, 'dashboard/validations_notes_president.html', context)


@login_required
def detail_promotion_notes(request, promotion_id):
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    promotion = get_object_or_404(Promotion.objects.select_related('filiere'), pk=promotion_id)
    
    # Étape 1: Récupérer les données de base (étudiants et cours)
    etudiants = Etudiant.objects.filter(
        inscriptions__promotion=promotion
    ).distinct().select_related('user').order_by('user__nom', 'user__postnom', 'user__prenom')
    
    # Filtrer les cours par année d'étude de la promotion
    if promotion.annee_etude_id:
        cours_list = Cours.objects.filter(
            filiere=promotion.filiere,
            annee_etude_id=promotion.annee_etude_id
        ).distinct().select_related('semestre', 'annee_etude').order_by('semestre__libelle', 'libelle')
    else:
        cours_list = Cours.objects.filter(
            filiere=promotion.filiere
        ).distinct().select_related('semestre', 'annee_etude').order_by('semestre__libelle', 'libelle')

    # Grouper les cours par semestre
    cours_par_semestre = {}
    for cours in cours_list:
        semestre_libelle = cours.semestre.libelle
        if semestre_libelle not in cours_par_semestre:
            cours_par_semestre[semestre_libelle] = []
        cours_par_semestre[semestre_libelle].append(cours)

    # Grouper les semestres par 2 pour l'affichage
    semestres_list = list(cours_par_semestre.items())
    semestres_groupes = []
    for i in range(0, len(semestres_list), 2):
        groupe = semestres_list[i:i+2]
        semestres_groupes.append(groupe)

    # Étape 2: Récupérer toutes les évaluations et notes pertinentes
    evaluations = Evaluation.objects.filter(cours__in=cours_list).select_related('type_evaluation', 'cours')
    cotations = Cotation.objects.filter(evaluation__in=evaluations, etudiant__in=etudiants)

    # Étape 3: Calculer la moyenne pondérée pour chaque étudiant et chaque cours
    moyennes_par_etudiant = {} # {etudiant_id: {cours_id: moyenne}}
    for cotation in cotations:
        etudiant_id = cotation.etudiant_id
        cours_id = cotation.evaluation.cours_id
        coeff = cotation.evaluation.coefficient
        note = float(cotation.note)

        # Initialiser le dictionnaire si nécessaire
        moyennes_par_etudiant.setdefault(etudiant_id, {})
        moyennes_par_etudiant[etudiant_id].setdefault(cours_id, {'total_pondere': 0, 'total_coeffs': 0})
        
        # Agréger les notes pondérées
        moyennes_par_etudiant[etudiant_id][cours_id]['total_pondere'] += note * coeff
        moyennes_par_etudiant[etudiant_id][cours_id]['total_coeffs'] += coeff

    # Étape 4: Préparer les lignes du tableau pour un affichage simple dans le template
    # Créer un dictionnaire de moyennes par cours pour un accès facile
    moyennes_dict = {}
    for etudiant in etudiants:
        moyennes_dict[etudiant.id] = {}
        for cours in cours_list:
            data = moyennes_par_etudiant.get(etudiant.id, {}).get(cours.id)
            moyenne = None
            if data and data.get('total_coeffs', 0) > 0:
                moyenne = round(data['total_pondere'] / data['total_coeffs'], 2)
            moyennes_dict[etudiant.id][cours.id] = moyenne
    
    lignes_tableau = []
    for etudiant in etudiants:
        lignes_tableau.append({
            'etudiant': etudiant,
            'moyennes': moyennes_dict[etudiant.id],
        })
    
    # Étape 5: Récupérer la liste des évaluations en attente pour les actions de validation
    evaluations_en_attente = evaluations.filter(
        is_published=False, 
        cotations__isnull=False
    ).distinct().annotate(
        nb_notes=Count('cotations'),
        moyenne=Avg('cotations__note'),
    )

    # Étape 6: Préparer le contexte final. Le tableau est toujours présent.
    context = {
        'promotion': promotion,
        'lignes_tableau': lignes_tableau,
        'cours_list': cours_list,
        'cours_par_semestre': cours_par_semestre,
        'semestres_groupes': semestres_groupes,
        'evaluations_en_attente': evaluations_en_attente,
    }
    return render(request, 'dashboard/detail_promotion_notes.html', context)

@login_required
def valider_toutes_evaluations_promotion(request, promotion_id):
    """Valider toutes les évaluations en attente d'une promotion"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    promotion = get_object_or_404(Promotion.objects.select_related('filiere'), pk=promotion_id)
    
    if request.method == 'POST':
        president = request.user.personnel
        
        # Récupérer les étudiants de cette promotion uniquement
        etudiants_promotion = Etudiant.objects.filter(
            inscriptions__promotion=promotion
        ).distinct()
        
        # Récupérer les étudiants des autres promotions de la même filière
        etudiants_autres_promotions = Etudiant.objects.filter(
            inscriptions__promotion__filiere=promotion.filiere
        ).exclude(
            inscriptions__promotion=promotion
        ).distinct()
        
        # Récupérer les évaluations de la filière en attente
        evaluations_en_attente = Evaluation.objects.filter(
            cours__filiere=promotion.filiere,
            is_published=False
        ).distinct()
        
        # Exclure les évaluations qui ont des notes pour des étudiants d'autres promotions
        if etudiants_autres_promotions.exists():
            evaluations_en_attente = evaluations_en_attente.exclude(
                cotations__etudiant__in=etudiants_autres_promotions
            )
        
        # Ne garder que les évaluations qui ont au moins une note pour cette promotion
        evaluations_a_valider = []
        for evaluation in evaluations_en_attente:
            if Cotation.objects.filter(evaluation=evaluation, etudiant__in=etudiants_promotion).exists():
                evaluations_a_valider.append(evaluation)
        
        count_validees = 0
        
        for evaluation in evaluations_a_valider:
            # Créer l'enregistrement de validation
            ValidationNotes.objects.create(
                evaluation=evaluation,
                validateur=president,
                commentaire=f"Validation automatique (lot) - Promotion {promotion.libelle}",
                est_valide=True
            )
            
            # Publier l'évaluation
            evaluation.is_published = True
            evaluation.published_at = timezone.now()
            evaluation.save()
            count_validees += 1
        
        if count_validees > 0:
            messages.success(request, f"{count_validees} évaluation(s) validée(s) et publiée(s) pour la promotion {promotion.libelle}.")
        else:
            messages.info(request, "Aucune évaluation à valider pour cette promotion.")
        
        return redirect('detail_promotion_notes', promotion_id=promotion.id)
    
    return redirect('detail_promotion_notes', promotion_id=promotion.id)

@login_required
def valider_evaluation(request, evaluation_id):
    """Valider ou rejeter une évaluation"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    evaluation = get_object_or_404(Evaluation, pk=evaluation_id)
    president = request.user.personnel

    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire = request.POST.get('commentaire', '')

        if action == 'valider':
            # Créer l'enregistrement de validation
            ValidationNotes.objects.create(
                evaluation=evaluation,
                validateur=president,
                commentaire=commentaire,
                est_valide=True
            )
            
            # Publier l'évaluation
            evaluation.is_published = True
            evaluation.published_at = timezone.now()
            evaluation.save()
            
            messages.success(request, f"L'évaluation de {evaluation.cours.libelle} a été validée et publiée.")
        elif action == 'rejeter':
            # Créer l'enregistrement de rejet
            ValidationNotes.objects.create(
                evaluation=evaluation,
                validateur=president,
                commentaire=commentaire,
                est_valide=False
            )
            
            # Supprimer les notes pour permettre une nouvelle saisie
            Cotation.objects.filter(evaluation=evaluation).delete()
            
            messages.warning(request, f"L'évaluation de {evaluation.cours.libelle} a été rejetée. Les notes ont été supprimées.")

        # Rediriger vers la page de la promotion si possible, sinon vers la liste générale
        if evaluation.cours.filiere and evaluation.cours.filiere.promotion_set.first():
            promotion = evaluation.cours.filiere.promotion_set.first()
            return redirect('detail_promotion_notes', promotion_id=promotion.id)
        return redirect('liste_evaluations_a_valider')

    # GET: afficher le détail de l'évaluation
    cotations = Cotation.objects.filter(evaluation=evaluation).select_related(
        'etudiant', 'etudiant__user'
    ).order_by('etudiant__user__nom', 'etudiant__user__postnom')

    context = {
        'evaluation': evaluation
    }
    return render(request, 'dashboard/valider_evaluation.html', context)

@login_required
def historique_validations(request):
    """Historique des validations effectuées par le président"""
    if not (hasattr(request.user, 'personnel') and request.user.has_role('president')):
        messages.error(request, "Accès réservé au président.")
        return redirect('dashboard')

    validations = ValidationNotes.objects.filter(
        validateur=request.user.personnel,
    ).select_related('evaluation__cours__filiere', 'validateur__user').order_by('-date_validation')

    # Calculer les statistiques
    total_validations = validations.count()
    validations_validees = validations.filter(est_valide=True).count()
    validations_rejetees = validations.filter(est_valide=False).count()

    context = {
        'validations': validations,
        'total_validations': total_validations,
        'validations_validees': validations_validees,
        'validations_rejetees': validations_rejetees,
    }
    return render(request, 'dashboard/historique_validations.html', context)

@login_required
def publier_horaires_examens(request):
    if not request.user.has_role('chef de filière'):
        messages.error(request, "Accès réservé au chef de filière.")
        return redirect('dashboard')

    chef_personnel = getattr(request.user, 'personnel', None)
    filieres = Filiere.objects.filter(chef=chef_personnel).order_by('libelle', 'code') if chef_personnel else Filiere.objects.none()
    examens = Evaluation.objects.filter(cours__filiere__in=filieres).select_related('cours', 'type_evaluation').order_by('date', 'cours__libelle')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('examens')
        if selected_ids:
            updated = Evaluation.objects.filter(pk__in=selected_ids, cours__filiere__in=filieres).update(is_published=True, published_at=timezone.now())
            messages.success(request, f"{updated} horaire(s) d'examen publié(s) avec succès.")
        else:
            messages.error(request, "Sélectionnez au moins un examen à publier.")
        return redirect('publier_horaires_examens')

    return render(request, 'results/publier_horaires_examens.html', {'examens': examens, 'filieres': filieres})

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Accès réservé au personnel.")
        return redirect('dashboard')

class BaseCRUDListView(StaffRequiredMixin, ListView):
    template_name = 'crud/list.html'
    context_object_name = 'object_list'

    def get_fields(self):
        """Retourne la liste des (nom_du_champ, libellé) pour l'affichage"""
        model = self.model
        return [(f.name, f.verbose_name.title()) for f in model._meta.fields]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', self.model._meta.verbose_name_plural.title()),
            'singular_name': getattr(self, 'singular_name', self.model._meta.verbose_name.title()),
            'create_url_name': getattr(self, 'create_url_name', ''),
            'update_url_name': getattr(self, 'update_url_name', ''),
            'delete_url_name': getattr(self, 'delete_url_name', ''),
            'fields': self.get_fields(),
        })
        return context

class BaseCRUDFormView(StaffRequiredMixin):
    template_name = 'crud/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', self.model._meta.verbose_name.title()),
            'action': getattr(self, 'action', 'Enregistrer'),
        })
        return context

class BaseCRUDCreateView(BaseCRUDFormView, CreateView):
    pass

class BaseCRUDUpdateView(BaseCRUDFormView, UpdateView):
    pass

class BaseCRUDDeleteView(StaffRequiredMixin, DeleteView):
    template_name = 'crud/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', self.model._meta.verbose_name.title()),
            'singular_name': getattr(self, 'singular_name', self.model._meta.verbose_name.title()),
            'list_url_name': getattr(self, 'list_url_name', ''),
        })
        return context

class FiliereListView(BaseCRUDListView):
    model = Filiere
    model_name = 'Filières'
    singular_name = 'Filière'
    create_url_name = 'filiere_create'
    update_url_name = 'filiere_update'
    delete_url_name = 'filiere_delete'

class FiliereCreateView(BaseCRUDCreateView):
    model = Filiere
    fields = ['code', 'libelle', 'description', 'chef']
    success_url = reverse_lazy('filiere_list')
    model_name = 'Filière'
    action = 'Ajouter'

class FiliereUpdateView(BaseCRUDUpdateView):
    model = Filiere
    fields = ['code', 'libelle', 'description', 'chef']
    success_url = reverse_lazy('filiere_list')
    model_name = 'Filière'
    action = 'Modifier'

class FiliereDeleteView(BaseCRUDDeleteView):
    model = Filiere
    success_url = reverse_lazy('filiere_list')
    model_name = 'Filière'
    singular_name = 'Filière'
    list_url_name = 'filiere_list'

class PromotionListView(BaseCRUDListView):
    model = Promotion
    model_name = 'Promotions'
    singular_name = 'Promotion'
    create_url_name = 'promotion_create'
    update_url_name = 'promotion_update'
    delete_url_name = 'promotion_delete'

class PromotionCreateView(BaseCRUDCreateView):
    model = Promotion
    fields = ['filiere', 'libelle']
    success_url = reverse_lazy('promotion_list')
    model_name = 'Promotion'
    action = 'Ajouter'

class PromotionUpdateView(BaseCRUDUpdateView):
    model = Promotion
    fields = ['filiere', 'libelle']
    success_url = reverse_lazy('promotion_list')
    model_name = 'Promotion'
    action = 'Modifier'

class PromotionDeleteView(BaseCRUDDeleteView):
    model = Promotion
    success_url = reverse_lazy('promotion_list')
    model_name = 'Promotion'
    singular_name = 'Promotion'
    list_url_name = 'promotion_list'

class CoursListView(BaseCRUDListView):
    model = Cours
    model_name = 'Cours'
    singular_name = 'Cours'
    create_url_name = 'cours_create'
    update_url_name = 'cours_update'
    delete_url_name = 'cours_delete'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['semestres'] = Semestre.objects.all().order_by('libelle')
        context['selected_semestre'] = self.request.GET.get('semestre')
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related('filiere', 'semestre', 'annee_etude')
        semestre_id = self.request.GET.get('semestre')
        if semestre_id:
            queryset = queryset.filter(semestre_id=semestre_id)
        return queryset

class CoursCreateView(BaseCRUDCreateView):
    model = Cours
    fields = ['filiere', 'semestre', 'annee_etude', 'code', 'libelle', 'volume_horaire']
    success_url = reverse_lazy('cours_list')
    model_name = 'Cours'
    action = 'Ajouter'

class CoursUpdateView(BaseCRUDUpdateView):
    model = Cours
    fields = ['filiere', 'semestre', 'annee_etude', 'code', 'libelle', 'volume_horaire']
    success_url = reverse_lazy('cours_list')
    model_name = 'Cours'
    action = 'Modifier'

class CoursDetailView(StaffRequiredMixin, DetailView):
    model = Cours
    template_name = 'crud/cours_detail.html'
    context_object_name = 'cours'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cours = self.object
        context.update({
            'model_name': 'Cours',
            'singular_name': 'Cours',
            'evaluations': cours.evaluation_set.select_related('type_evaluation').all(),
        })
        return context

class CoursDeleteView(BaseCRUDDeleteView):
    model = Cours
    success_url = reverse_lazy('cours_list')
    model_name = 'Cours'
    singular_name = 'Cours'
    list_url_name = 'cours_list'

class TypeEvaluationListView(BaseCRUDListView):
    model = TypeEvaluation
    model_name = 'Types d\'évaluation'
    singular_name = 'Type d\'évaluation'
    create_url_name = 'typeevaluation_create'
    update_url_name = 'typeevaluation_update'
    delete_url_name = 'typeevaluation_delete'

class TypeEvaluationCreateView(BaseCRUDCreateView):
    model = TypeEvaluation
    fields = ['libelle']
    success_url = reverse_lazy('typeevaluation_list')
    model_name = 'Type d\'évaluation'
    action = 'Ajouter'

class TypeEvaluationUpdateView(BaseCRUDUpdateView):
    model = TypeEvaluation
    fields = ['libelle']
    success_url = reverse_lazy('typeevaluation_list')
    model_name = 'Type d\'évaluation'
    action = 'Modifier'

class TypeEvaluationDeleteView(BaseCRUDDeleteView):
    model = TypeEvaluation
    success_url = reverse_lazy('typeevaluation_list')
    model_name = 'Type d\'évaluation'
    singular_name = 'Type d\'évaluation'
    list_url_name = 'typeevaluation_list'

class EvaluationListView(BaseCRUDListView):
    model = Evaluation
    model_name = 'Évaluations'
    singular_name = 'Évaluation'
    create_url_name = 'evaluation_create'
    update_url_name = 'evaluation_update'
    delete_url_name = 'evaluation_delete'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('cours', 'cours__filiere', 'type_evaluation')
        filiere_id = self.request.GET.get('filiere')
        if filiere_id:
            queryset = queryset.filter(cours__filiere_id=filiere_id)
        return queryset

class EvaluationCreateView(BaseCRUDCreateView):
    model = Evaluation
    fields = ['type_evaluation', 'cours', 'date']
    success_url = reverse_lazy('evaluation_list')
    model_name = 'Évaluation'
    action = 'Ajouter'

class EvaluationUpdateView(BaseCRUDUpdateView):
    model = Evaluation
    fields = ['type_evaluation', 'cours', 'date']
    success_url = reverse_lazy('evaluation_list')
    model_name = 'Évaluation'
    action = 'Modifier'

class EvaluationDeleteView(BaseCRUDDeleteView):
    model = Evaluation
    success_url = reverse_lazy('evaluation_list')
    model_name = 'Évaluation'
    singular_name = 'Évaluation'
    list_url_name = 'evaluation_list'

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.has_role('president') # type: ignore[attr-defined]

    def handle_no_permission(self):
        self.request.user.is_authenticated # type: ignore[attr-defined]
        messages.error(self.request, "Accès réservé à l'administrateur ou au président.")
        return redirect('dashboard')

class UserListView(AdminRequiredMixin, BaseCRUDListView):
    model = User
    model_name = 'Utilisateurs'
    singular_name = 'Utilisateur'
    create_url_name = 'user_create'
    update_url_name = 'user_update'
    delete_url_name = 'user_delete'

    def get_queryset(self):
        return User.objects.all().order_by('-is_active', 'nom', 'prenom')

    def get_fields(self):
        return [
            ('username', "Nom d'utilisateur"),
            ('nom', 'Nom'),
            ('prenom', 'Prénom'),
            ('email', 'Email'),
            ('get_roles_display', 'Rôles'),
            ('is_active', 'Actif'),
            ('is_validated', 'Validé'),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extra_fields'] = ['is_staff', 'is_superuser']
        return context

    def get_roles_display(self, obj):
        return ", ".join(obj.role_labels) if obj.role_labels else "-"
    get_roles_display.short_description = 'Rôles'

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    template_name = 'crud/user_form.html'
    fields = ['username', 'email', 'nom', 'postnom', 'prenom', 'sexe', 'tel', 'mat', 'adresse', 'is_active', 'is_validated', 'is_staff', 'is_superuser']
    success_url = reverse_lazy('user_list')
    model_name = 'Utilisateur'
    action = 'Ajouter'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password('demo')
        user.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Utilisateur'),
            'action': getattr(self, 'action', 'Ajouter'),
        })
        return context

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    template_name = 'crud/user_form.html'
    fields = ['username', 'email', 'nom', 'postnom', 'prenom', 'sexe', 'tel', 'mat', 'adresse', 'is_active', 'is_validated', 'is_staff', 'is_superuser']
    success_url = reverse_lazy('user_list')
    model_name = 'Utilisateur'
    action = 'Modifier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Utilisateur'),
            'action': getattr(self, 'action', 'Modifier'),
        })
        return context

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('user_list')
    template_name = 'crud/confirm_delete.html'
    model_name = 'Utilisateur'
    singular_name = 'Utilisateur'
    list_url_name = 'user_list'

class PersonnelListView(AdminRequiredMixin, BaseCRUDListView):
    model = Personnel
    model_name = 'Personnels'
    singular_name = 'Personnel'
    create_url_name = 'personnel_create'
    update_url_name = 'personnel_update'
    delete_url_name = 'personnel_delete'

    def get_fields(self):
        return [
            ('user', 'Utilisateur'),
            ('fonction', 'Fonction'),
            ('grade', 'Grade'),
        ]

    def get_user(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user.short_description = 'Utilisateur'

class PersonnelCreateView(AdminRequiredMixin, CreateView):
    model = Personnel
    template_name = 'crud/form.html'
    fields = ['user', 'fonction', 'grade']
    success_url = reverse_lazy('personnel_list')
    model_name = 'Personnel'
    action = 'Ajouter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Personnel'),
            'action': getattr(self, 'action', 'Ajouter'),
        })
        return context

class PersonnelUpdateView(AdminRequiredMixin, UpdateView):
    model = Personnel
    template_name = 'crud/form.html'
    fields = ['user', 'fonction', 'grade']
    success_url = reverse_lazy('personnel_list')
    model_name = 'Personnel'
    action = 'Modifier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Personnel'),
            'action': getattr(self, 'action', 'Modifier'),
        })
        return context

class PersonnelDeleteView(AdminRequiredMixin, DeleteView):
    model = Personnel
    success_url = reverse_lazy('personnel_list')
    template_name = 'crud/confirm_delete.html'
    model_name = 'Personnel'
    singular_name = 'Personnel'
    list_url_name = 'personnel_list'

class ChefFiliereOrAdminMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_role('chef de filière')

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Accès réservé à l'administrateur ou au chef de filière.")
        return redirect('dashboard')

class EtudiantListView(ChefFiliereOrAdminMixin, BaseCRUDListView):
    model = Etudiant
    model_name = 'Étudiants'
    singular_name = 'Étudiant'
    create_url_name = 'etudiant_create'
    update_url_name = 'etudiant_update'
    delete_url_name = 'etudiant_delete'

    def get_fields(self):
        return []

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        if self.request.user.has_role('chef de filière') and not self.request.user.is_superuser:
            chef_personnel = getattr(self.request.user, 'personnel', None)
            if chef_personnel:
                chef_filieres = Filiere.objects.filter(chef=chef_personnel)
                queryset = queryset.filter(inscriptions__promotion__filiere__in=chef_filieres).distinct()
        return queryset

    def get_user(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_user.short_description = 'Utilisateur'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Ajouter les filtres par promotion
        if self.request.user.has_role('chef de filière') and not self.request.user.is_superuser:
            chef_personnel = getattr(self.request.user, 'personnel', None)
            if chef_personnel:
                chef_filieres = Filiere.objects.filter(chef=chef_personnel)
                context['promotions'] = Promotion.objects.filter(filiere__in=chef_filieres).distinct().order_by('libelle')
        else:
            context['promotions'] = Promotion.objects.all().order_by('libelle')

        # Filtrer par promotion si spécifié dans l'URL
        promotion_id = self.request.GET.get('promotion')
        if promotion_id:
            context['selected_promotion'] = int(promotion_id)
            # Appliquer le filtre directement sur le queryset
            context['object_list'] = context['object_list'].filter(inscriptions__promotion_id=promotion_id).distinct()
        else:
            context['selected_promotion'] = None

        return context

class EtudiantCreateView(AdminRequiredMixin, CreateView):
    model = Etudiant
    template_name = 'crud/form.html'
    fields = ['user', 'matricule']
    success_url = reverse_lazy('etudiant_list')
    model_name = 'Étudiant'
    action = 'Ajouter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Étudiant'),
            'action': getattr(self, 'action', 'Ajouter'),
        })
        return context

class EtudiantUpdateView(AdminRequiredMixin, UpdateView):
    model = Etudiant
    template_name = 'crud/form.html'
    fields = ['user', 'matricule']
    success_url = reverse_lazy('etudiant_list')
    model_name = 'Étudiant'
    action = 'Modifier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Étudiant'),
            'action': getattr(self, 'action', 'Modifier'),
        })
        return context

class EtudiantDetailView(ChefFiliereOrAdminMixin, DetailView):
    model = Etudiant
    template_name = 'crud/etudiant_detail.html'
    context_object_name = 'etudiant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        etudiant = self.object
        context.update({
            'model_name': 'Étudiant',
            'singular_name': 'Étudiant',
            'inscriptions': etudiant.inscriptions.select_related('promotion').all(),
            'cotations': etudiant.cotations.select_related('evaluation', 'evaluation__cours').all(),
        })
        return context

class EtudiantDeleteView(AdminRequiredMixin, DeleteView):
    model = Etudiant
    success_url = reverse_lazy('etudiant_list')
    template_name = 'crud/confirm_delete.html'
    model_name = 'Étudiant'
    singular_name = 'Étudiant'
    list_url_name = 'etudiant_list'

class RoleListView(AdminRequiredMixin, BaseCRUDListView):
    model = Role
    model_name = 'Rôles'
    singular_name = 'Rôle'
    create_url_name = 'role_create'
    update_url_name = 'role_update'
    delete_url_name = 'role_delete'

class RoleCreateView(AdminRequiredMixin, CreateView):
    model = Role
    template_name = 'crud/form.html'
    fields = ['libelle']
    success_url = reverse_lazy('role_list')
    model_name = 'Rôle'
    action = 'Ajouter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Rôle'),
            'action': getattr(self, 'action', 'Ajouter'),
        })
        return context

class RoleUpdateView(AdminRequiredMixin, UpdateView):
    model = Role
    template_name = 'crud/form.html'
    fields = ['libelle']
    success_url = reverse_lazy('role_list')
    model_name = 'Rôle'
    action = 'Modifier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Rôle'),
            'action': getattr(self, 'action', 'Modifier'),
        })
        return context

class RoleDeleteView(AdminRequiredMixin, DeleteView):
    model = Role
    success_url = reverse_lazy('role_list')
    template_name = 'crud/confirm_delete.html'
    model_name = 'Rôle'
    singular_name = 'Rôle'
    list_url_name = 'role_list'

class FonctionListView(AdminRequiredMixin, BaseCRUDListView):
    model = Fonction
    model_name = 'Fonctions'
    singular_name = 'Fonction'
    create_url_name = 'fonction_create'
    update_url_name = 'fonction_update'
    delete_url_name = 'fonction_delete'

class FonctionCreateView(AdminRequiredMixin, CreateView):
    model = Fonction
    template_name = 'crud/form.html'
    fields = ['intitule']
    success_url = reverse_lazy('fonction_list')
    model_name = 'Fonction'
    action = 'Ajouter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Fonction'),
            'action': getattr(self, 'action', 'Ajouter'),
        })
        return context

class FonctionUpdateView(AdminRequiredMixin, UpdateView):
    model = Fonction
    template_name = 'crud/form.html'
    fields = ['intitule']
    success_url = reverse_lazy('fonction_list')
    model_name = 'Fonction'
    action = 'Modifier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'model_name': getattr(self, 'model_name', 'Fonction'),
            'action': getattr(self, 'action', 'Modifier'),
        })
        return context

class FonctionDeleteView(AdminRequiredMixin, DeleteView):
    model = Fonction
    success_url = reverse_lazy('fonction_list')
    template_name = 'crud/confirm_delete.html'
    model_name = 'Fonction'
    singular_name = 'Fonction'
    list_url_name = 'fonction_list'
