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

@register.filter
def subtract(value, arg):
    """Soustrait deux valeurs"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def last_item(lst):
    """Récupère le dernier élément d'une liste de manière sécurisée"""
    try:
        if not lst:
            return None
        return list(lst)[-1]
    except (IndexError, TypeError, ValueError):
        return None

@register.filter
def get_item(dictionary, key):
    """Récupère une valeur d'un dictionnaire par sa clé"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None
