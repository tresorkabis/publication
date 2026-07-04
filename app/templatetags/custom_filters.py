from django import template

register = template.Library()

@register.filter
def get_attr(obj, field_name):
    """Récupère un attribut d'un objet"""
    try:
        return getattr(obj, field_name)
    except AttributeError:
        return None