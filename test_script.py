import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()

from django.db import connection

# Vérifier les tables
tables = connection.introspection.table_names()
print("Tables dans la base de données:")
for t in sorted(tables):
    print(f"  - {t}")

print("\n" + "="*60)
print("Exécution de create_demo_student...")
print("="*60)

from create_demo_student import create_demo_student
create_demo_student()