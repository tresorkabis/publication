import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from app.models import Filiere

filieres = Filiere.objects.all()
count = filieres.count()

result = f"\nNombre de filières: {count}\n"
if count > 0:
    result += "\nListe des filières:\n"
    for f in filieres:
        result += f"  - {f.libelle} ({f.code})\n"
else:
    result += "\nAucune filière enregistrée.\n"

print(result)

# Écrire dans un fichier pour pouvoir le lire
with open('filieres_result.txt', 'w', encoding='utf-8') as file:
    file.write(result)