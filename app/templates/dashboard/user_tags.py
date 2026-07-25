from django import template

register = template.Library()

@register.simple_tag
def get_user_display_role(user):
    """
    Retourne le rôle principal d'un utilisateur pour l'affichage,
    en donnant la priorité aux rôles du personnel.
    """
    if hasattr(user, 'personnel'):
        if user.has_role('chef de filière'):
            return 'Chef de Filière'
        if user.has_role('enseignant'):
            return 'Enseignant'
    if hasattr(user, 'etudiant'):
        return 'Étudiant'
    if user.is_superuser:
        return 'Super Admin'
    if user.is_staff:
        return 'Staff'
    return "Utilisateur"