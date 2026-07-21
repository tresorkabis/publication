from django import template

register = template.Library()

@register.filter
def get_attr(obj, field_name):
    """Récupère un attribut ou appelle une méthode d'un objet"""
    try:
        attr = getattr(obj, field_name)
        if callable(attr):
            result = attr()
            return result
        return attr
    except AttributeError:
        return None
