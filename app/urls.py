from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/upload-photo/', views.upload_photo, name='upload_photo'),
    path('results/', views.results_list, name='results_list'),
    path('results/print/', views.print_results, name='print_results'),
    path('results/enter-marks/<int:evaluation_id>/', views.enter_marks, name='enter_marks'),
    path('results/manage-marks/<int:evaluation_id>/', views.manage_marks, name='manage_marks'),
    path('results/edit-mark/<int:cotation_id>/', views.edit_mark, name='edit_mark'),
    path('results/delete-mark/<int:cotation_id>/', views.delete_mark, name='delete_mark'),
    path('results/publish/<int:evaluation_id>/', views.publish_evaluation, name='publish_evaluation'),
    path('validations/', views.pending_validations, name='pending_validations'),
    path('validations/validate/<int:user_id>/', views.validate_user, name='validate_user'),

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