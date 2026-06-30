from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('inscription/', views.register, name='register'),
    path('connexion/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profil/', views.profile, name='profile'),
    path('profil/photo/', views.upload_photo, name='upload_photo'),
    path('resultats/', views.results_list, name='results_list'),
    path('resultats/imprimer/', views.print_results, name='print_results'),
    path('resultats/saisir-notes/<int:evaluation_id>/', views.enter_marks, name='enter_marks'),
    path('resultats/gerer-notes/<int:evaluation_id>/', views.manage_marks, name='manage_marks'),
    path('resultats/modifier-note/<int:cotation_id>/', views.edit_mark, name='edit_mark'),
    path('resultats/supprimer-note/<int:cotation_id>/', views.delete_mark, name='delete_mark'),
    path('resultats/publier/<int:evaluation_id>/', views.publish_evaluation, name='publish_evaluation'),
    path('validations/', views.pending_validations, name='pending_validations'),
    path('validations/valider/<int:user_id>/', views.validate_user, name='validate_user'),

    path('filieres/', views.FiliereListView.as_view(), name='filiere_list'),
    path('filieres/ajouter/', views.FiliereCreateView.as_view(), name='filiere_create'),
    path('filieres/<int:pk>/modifier/', views.FiliereUpdateView.as_view(), name='filiere_update'),
    path('filieres/<int:pk>/supprimer/', views.FiliereDeleteView.as_view(), name='filiere_delete'),

    path('promotions/', views.PromotionListView.as_view(), name='promotion_list'),
    path('promotions/ajouter/', views.PromotionCreateView.as_view(), name='promotion_create'),
    path('promotions/<int:pk>/modifier/', views.PromotionUpdateView.as_view(), name='promotion_update'),
    path('promotions/<int:pk>/supprimer/', views.PromotionDeleteView.as_view(), name='promotion_delete'),

    path('cours/', views.CoursListView.as_view(), name='cours_list'),
    path('cours/ajouter/', views.CoursCreateView.as_view(), name='cours_create'),
    path('cours/<int:pk>/modifier/', views.CoursUpdateView.as_view(), name='cours_update'),
    path('cours/<int:pk>/supprimer/', views.CoursDeleteView.as_view(), name='cours_delete'),

    path('types-evaluation/', views.TypeEvaluationListView.as_view(), name='typeevaluation_list'),
    path('types-evaluation/ajouter/', views.TypeEvaluationCreateView.as_view(), name='typeevaluation_create'),
    path('types-evaluation/<int:pk>/modifier/', views.TypeEvaluationUpdateView.as_view(), name='typeevaluation_update'),
    path('types-evaluation/<int:pk>/supprimer/', views.TypeEvaluationDeleteView.as_view(), name='typeevaluation_delete'),

    path('evaluations/', views.EvaluationListView.as_view(), name='evaluation_list'),
    path('evaluations/ajouter/', views.EvaluationCreateView.as_view(), name='evaluation_create'),
    path('evaluations/<int:pk>/modifier/', views.EvaluationUpdateView.as_view(), name='evaluation_update'),
    path('evaluations/<int:pk>/supprimer/', views.EvaluationDeleteView.as_view(), name='evaluation_delete'),
]