from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import (
    Role, UtilisateurRole, Fonction, Personnel, Etudiant,
    Filiere, Promotion, Inscription, Semestre, Cours, TypeEvaluation,
    Evaluation, Cotation
)
from django.utils import timezone
import random
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données de démonstration pour l\'application ESFORCA'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Génération des données de démonstration...")
        
        # Créer les rôles par défaut
        self.create_default_roles()
        
        # Créer les utilisateurs
        self.create_users()
        
        # Créer les filières et chefs
        self.create_filieres()
        
        # Créer les promotions
        self.create_promotions()
        
        # Créer les cours
        self.create_cours()
        
        # Créer les évaluations
        self.create_evaluations()
        
        # Créer les cotations
        self.create_cotations()
        
        self.stdout.write(self.style.SUCCESS("✅ Données de démonstration générées avec succès!"))

    def create_default_roles(self):
        for role_libelle in Role.default_roles():
            Role.ensure_default_roles()

    def create_users(self):
        emails = [
            'admin@example.com', 'secretaire@example.com', 'president@example.com',
            'enseignant1@example.com', 'enseignant2@example.com', 'chef_filiere@example.com'
        ]
        
    def create_users(self):
        emails = [
            'admin@example.com', 'secretaire@example.com', 'president@example.com',
            'enseignant1@example.com', 'enseignant2@example.com', 'chef_filiere@example.com'
        ]
        
        for email in emails:
            username = f"user_{random.randint(1000,9999)}"
            user = User.objects.create_user(
                email=email,
                username=username,
                password='password123'
            )
            
            # Attribuer des rôles
            for role in Role.objects.all():
                UtilisateurRole.objects.get_or_create(user=user, role=role)

    def create_filieres(self):
        filieres = [
            {'code': 'INF', 'libelle': 'Informatique', 'chef': None},
            {'code': 'MATH', 'libelle': 'Mathématiques', 'chef': None},
            {'code': 'PHY', 'libelle': 'Physique', 'chef': None}
        ]
        
        # Créer un utilisateur chef s'il n'existe pas
        chef_email = 'chef_filiere@example.com'
        if not User.objects.filter(email=chef_email).exists():
            admin_user = User.objects.create_superuser(
                email=chef_email,
                username='chef_admin',
                password='password123'
            )
        else:
            admin_user = User.objects.get(email=chef_email)
        
        chef_role, _ = Role.objects.get_or_create(libelle='chef de filière')
        chef_personnel, _ = Personnel.objects.get_or_create(
            user=admin_user,
            defaults={'fonction': None, 'grade': 'Chef de filière'}
        )
        UtilisateurRole.objects.get_or_create(user=admin_user, role=chef_role)

        for f in filieres:
            Filiere.objects.create(
                codfiliere=f['code'],
                libelle=f['libelle'],
                chef=chef_personnel
            )

    def create_promotions(self):
        filieres = Filiere.objects.all()
        for f in filieres:
            for annee in range(2020, 2025):
                Promotion.objects.create(
                    filiere=f,
                    libnom=f'Promo {f.libelle} {annee}',
                    annee=annee,
                    niveau='Licence'
                )

    def create_cours(self):
        semestres = [
            {'libelle': 'S1', 'datedeb': '2023-09-01', 'datefin': '2024-01-31'},
            {'libelle': 'S2', 'datedeb': '2024-02-01', 'datefin': '2024-06-30'}
        ]
        for s in semestres:
            Semestre.objects.create(**s)
            
        for f in Filiere.objects.all():
            for s in Semestre.objects.all():
                for i in range(1, 6):
                    Cours.objects.create(
                        filiere=f,
                        semestre=s,
                        codcours=f'COURS{f.codfiliere}{i:02d}',
                        libelle=f'Cours {i} de {f.libelle}'
                    )

    def create_evaluations(self):
        type_evals = []
        for i in range(1, 11):
            te, _ = TypeEvaluation.objects.get_or_create(libelle=f'Évaluation {i}')
            type_evals.append(te)
        
        for c in Cours.objects.all():
            for _ in range(2):  # 2 évaluations par cours
                Evaluation.objects.create(
                    type_eval=random.choice(type_evals),
                    cours=c,
                    lib=f'Évaluation {c.libelle} {random.randint(1,10)}',
                    coefficient=random.randint(1,5),
                    duree=None
                )

    def create_cotations(self):
        for e in Evaluation.objects.all():
            for s in Etudiant.objects.all():
                Cotation.objects.get_or_create(
                    etudiant=s,
                    evaluation=e,
                    defaults={'note': round(random.uniform(0, 20), 2)}
                )
