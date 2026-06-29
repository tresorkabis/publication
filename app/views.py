from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import UserRegistrationForm, UserProfileForm
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
        'recent_evaluations': Evaluation.objects.select_related('cours', 'type_eval').order_by('-idevaluation')[:5],
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
    user = request.user
    context = {}
    if hasattr(user, 'etudiant'):
        context['is_student'] = True
        context['etudiant'] = user.etudiant
        context['inscriptions'] = Inscription.objects.filter(etudiant=user.etudiant)
        context['cotations'] = Cotation.objects.filter(
            etudiant=user.etudiant,
            evaluation__is_published=True
        ).select_related('evaluation', 'evaluation__cours')
    elif hasattr(user, 'personnel'):
        context['is_staff'] = True
        context['personnel'] = user.personnel
        # Pour le personnel, on montre les évaluations qu'ils peuvent gérer
        context['evaluations'] = Evaluation.objects.all().select_related('cours', 'type_eval')
    else:
        # Chef de filière
        from .models import ChefFiliere
        try:
            chef = ChefFiliere.objects.get(user=user)
        except ChefFiliere.DoesNotExist:
            chef = None

        if chef is not None:
            context['is_chef'] = True
            context['chef'] = chef
            context['filieres'] = chef.filieres_dirigees.all()
            # Un chef peut voir toutes les évaluations des filières qu'il dirige
            context['evaluations'] = Evaluation.objects.filter(cours__filiere__in=context['filieres']).select_related('cours', 'type_eval')
            context['unpublished_evaluations'] = Evaluation.objects.filter(
                cours__filiere__in=context['filieres'],
                is_published=False,
                cotation__isnull=False
            ).distinct().select_related('cours')
    return render(request, 'dashboard.html', context)

@login_required
def pending_validations(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    users = User.objects.filter(is_active=False, is_validated=False).order_by('date_joined')
    return render(request, 'pending_validations.html', {'users': users})

@login_required
def validate_user(request, user_id):
    if not request.user.is_staff:
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
            etudiant=request.user.etudiant,
            evaluation__is_published=True
        ).select_related('evaluation', 'evaluation__cours')
        return render(request, 'results/student_results.html', {'cotations': cotations})
    
    return redirect('dashboard')

@login_required
def enter_marks(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') or hasattr(request.user, 'cheffiliere')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')
    
    evaluation = Evaluation.objects.get(pk=evaluation_id)
    students = Etudiant.objects.filter(inscription__promotion__filiere=evaluation.cours.filiere).distinct()
    
    if request.method == 'POST':
        for student in students:
            note = request.POST.get(f'note_{student.id}')
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
        ).select_related('evaluation', 'evaluation__cours', 'evaluation__type_eval')
        return render(request, 'results/print_results.html', {'cotations': cotations, 'today': timezone.now()})
    return redirect('dashboard')

@login_required
def edit_mark(request, cotation_id):
    if not (hasattr(request.user, 'personnel') or hasattr(request.user, 'cheffiliere')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')
    
    cotation = Cotation.objects.get(pk=cotation_id)
    if request.method == 'POST':
        note = request.POST.get('note')
        if note:
            cotation.note = note
            cotation.save()
            messages.success(request, "La note a été modifiée.")
            return redirect('manage_marks', evaluation_id=cotation.evaluation.idevaluation)
            
    return render(request, 'results/edit_mark.html', {'cotation': cotation})

@login_required
def delete_mark(request, cotation_id):
    if not (hasattr(request.user, 'personnel') or hasattr(request.user, 'cheffiliere')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')
    
    cotation = Cotation.objects.get(pk=cotation_id)
    eval_id = cotation.evaluation.idevaluation
    cotation.delete()
    messages.success(request, "La note a été supprimée.")
    return redirect('manage_marks', evaluation_id=eval_id)

@login_required
def manage_marks(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') or hasattr(request.user, 'cheffiliere')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')
    
    evaluation = Evaluation.objects.get(pk=evaluation_id)
    cotations = Cotation.objects.filter(evaluation=evaluation).select_related('etudiant', 'etudiant__user')
    return render(request, 'results/manage_marks.html', {
        'evaluation': evaluation,
        'cotations': cotations,
    })

@login_required
def publish_evaluation(request, evaluation_id):
    from .models import ChefFiliere

    try:
        chef = ChefFiliere.objects.get(user=request.user)
    except ChefFiliere.DoesNotExist:
        messages.error(request, "Accès réservé au chef de filière.")
        return redirect('dashboard')

    evaluation = get_object_or_404(
        Evaluation,
        pk=evaluation_id,
        cours__filiere__in=chef.filieres_dirigees.all()
    )

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
