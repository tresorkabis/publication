# Script de test pour voir la structure des propositions d'un enseignant
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Personnel, User, ProposalCoursEnseignant

# Chercher l'enseignant Lumumba
users = User.objects.filter(username__contains='rtm2')
for u in users:
    print(f"User: {u.username} - {u.get_full_name()}")
    try:
        p = Personnel.objects.get(user=u)
        print(f"  Personnel ID: {p.idpersonnel}")
        props = ProposalCoursEnseignant.objects.filter(enseignant=p)
        print(f"  Propositions: {props.count()}")
        for prop in props:
            print(f"    ID={prop.id} - Cours: {prop.cours.libelle} - Accepte: {prop.est_accepte} - Date: {prop.date_proposition}")
    except Personnel.DoesNotExist:
        print(f"  Pas de profil Personnel")