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
]