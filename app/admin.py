from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UtilisateurRole, Fonction, Personnel, Etudiant, Filiere, Promotion, Inscription, Semestre, Cours, TypeEvaluation, Evaluation, Cotation, CalendrierAcademique, ProposalCoursEnseignant, AnneeEtude

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'postnom', 'prenom', 'sexe', 'tel', 'mat', 'email', 'adresse', 'photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Validation', {'fields': ('is_validated',)}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'nom', 'postnom', 'prenom', 'mat', 'email', 'is_staff', 'is_validated', 'get_roles')
    search_fields = ('username', 'nom', 'postnom', 'prenom', 'mat', 'email')

    def get_roles(self, obj):
        return ", ".join(obj.role_labels)
    get_roles.short_description = 'Rôles'

admin.site.register(Role)
admin.site.register(UtilisateurRole)
admin.site.register(Fonction)
admin.site.register(Personnel)
admin.site.register(Etudiant)
admin.site.register(Filiere)
admin.site.register(Promotion)
admin.site.register(Inscription)
admin.site.register(Semestre)
admin.site.register(Cours)
admin.site.register(TypeEvaluation)
admin.site.register(Evaluation)
admin.site.register(Cotation)
admin.site.register(CalendrierAcademique)
admin.site.register(ProposalCoursEnseignant)
admin.site.register(AnneeEtude)
