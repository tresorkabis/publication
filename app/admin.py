from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UtilisateurRole, Fonction, Personnel, Etudiant, ChefFiliere, Filiere, Promotion, Inscription, Semestre, Cours, TypeEvaluation, Evaluation, Cotation

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('nom', 'postnom', 'prenom', 'sexe', 'telephone', 'matricule', 'adresse', 'photo', 'is_validated')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('username', 'email', 'nom', 'postnom', 'prenom', 'sexe', 'telephone', 'matricule', 'adresse', 'photo', 'is_validated', 'password1', 'password2')}),
    )
    list_display = ('username', 'nom', 'prenom', 'matricule', 'email', 'is_staff', 'is_validated', 'get_roles')
    search_fields = ('username', 'nom', 'prenom', 'matricule', 'email')

    def get_roles(self, obj):
        return ", ".join(obj.role_labels)
    get_roles.short_description = 'Rôles'

admin.site.register(Role)
admin.site.register(UtilisateurRole)
admin.site.register(Fonction)
admin.site.register(Personnel)
admin.site.register(Etudiant)
admin.site.register(ChefFiliere)
admin.site.register(Filiere)
admin.site.register(Promotion)
admin.site.register(Inscription)
admin.site.register(Semestre)
admin.site.register(Cours)
admin.site.register(TypeEvaluation)
admin.site.register(Evaluation)
admin.site.register(Cotation)
