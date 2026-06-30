import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Q
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
    # Statistiques générales
    total_users = User.objects.count()
    total_students = Etudiant.objects.count()
    total_staff = Personnel.objects.count()
    total_filieres = Filiere.objects.count()

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
        'promotions_data': json.dumps(promotions_data),
        'students_count_data': json.dumps(students_count_data),
        'recent_inscriptions': recent_inscriptions,
        'recent_evaluations': recent_evaluations,
    }

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
        ).select_related('evaluation', 'evaluation__cours', 'evaluation__type_eval')
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
            return redirect('manage_marks', evaluation_id=cotation.evaluation.idevaluation)

    return render(request, 'results/edit_mark.html', {'cotation': cotation})

@login_required
def delete_mark(request, cotation_id):
    if not (hasattr(request.user, 'personnel') or request.user.has_role('chef de filière')):
        messages.error(request, "Accès réservé au personnel ou aux chefs de filière.")
        return redirect('dashboard')

    cotation = Cotation.objects.get(pk=cotation_id)
    eval_id = cotation.evaluation.idevaluation
    cotation.delete()
    messages.success(request, "La note a été supprimée.")
    return redirect('manage_marks', evaluation_id=eval_id)

@login_required
def manage_marks(request, evaluation_id):
    if not (hasattr(request.user, 'personnel') or request.user.has_role('chef de filière')):
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
    if not (hasattr(request.user, 'personnel') and request.user.has_role('chef de filière')):
        messages.error(request, "Accès réservé au chef de filière.")
        return redirect('dashboard')

    chef_personnel = request.user.personnel
    evaluation = get_object_or_404(
        Evaluation,
        pk=evaluation_id,
        cours__filiere__in=chef_personnel.filieres_dirigees.all()
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

class CoursCreateView(BaseCRUDCreateView):
    model = Cours
    fields = ['filiere', 'semestre', 'code', 'libelle', 'volume_horaire']
    success_url = reverse_lazy('cours_list')
    model_name = 'Cours'
    action = 'Ajouter'

class CoursUpdateView(BaseCRUDUpdateView):
    model = Cours
    fields = ['filiere', 'semestre', 'code', 'libelle', 'volume_horaire']
    success_url = reverse_lazy('cours_list')
    model_name = 'Cours'
    action = 'Modifier'

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