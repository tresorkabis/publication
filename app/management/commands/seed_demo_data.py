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
        
        # Créer les filières
        self.create_filieres()
        
        # Créer les promotions
        self.create_promotions()
        
        # Créer les semestres
        self.create_semestres()
        
        # Créer les cours
        self.create_cours()
        
        # Créer les types d'évaluation
        self.create_type_evaluations()
        
        # Créer les évaluations
        self.create_evaluations()
        
        self.stdout.write(self.style.SUCCESS("✅ Données de démonstration générées avec succès!"))

    def create_default_roles(self):
        self.stdout.write("  📋 Création des rôles...")
        for libelle in Role.default_roles():
            Role.objects.get_or_create(libelle=libelle)

    def create_filieres(self):
        self.stdout.write("  🏛️ Création des filières, promotions et acteurs...")
        
        # === Filieres ===
        filieres_data = [
            {'code': 'INF', 'libelle': 'Informatique de Gestion'},
            {'code': 'MATH', 'libelle': 'Mathématiques et Applications'},
            {'code': 'PHY', 'libelle': 'Physique Fondamentale'},
            {'code': 'GEST', 'libelle': 'Gestion des Entreprises'},
            {'code': 'COM', 'libelle': 'Communication et Médias'},
        ]
        
        # === SUPER ADMIN ===
        admin_user, _ = User.objects.get_or_create(
            email='admin@esforca.cd',
            defaults={
                'username': 'admin',
                'nom': 'Admin',
                'postnom': 'System',
                'prenom': 'Super',
                'sexe': 'M',
                'tel': '+243800000001',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_validated': True,
            }
        )
        admin_user.set_password('demo')
        admin_user.save()
        
        # === ADMIN (sans superuser) ===
        admin2, _ = User.objects.get_or_create(
            email='admin2@esforca.cd',
            defaults={
                'username': 'admin2',
                'nom': 'Admin2',
                'postnom': 'System',
                'prenom': 'Junior',
                'sexe': 'F',
                'tel': '+243800000002',
                'is_staff': True,
                'is_active': True,
                'is_validated': True,
            }
        )
        admin2.set_password('demo')
        admin2.save()
        role_admin, _ = Role.objects.get_or_create(libelle='administrateur')
        UtilisateurRole.objects.get_or_create(user=admin2, role=role_admin)
        
        # === SECRETAIRE ===
        secretaire_user, _ = User.objects.get_or_create(
            email='secretaire@esforca.cd',
            defaults={
                'username': 'secretaire',
                'nom': 'Mukendi',
                'postnom': 'Kabasele',
                'prenom': 'Esther',
                'sexe': 'F',
                'tel': '+243800000003',
                'is_staff': True,
                'is_active': True,
                'is_validated': True,
            }
        )
        secretaire_user.set_password('demo')
        secretaire_user.save()
        role_sec, _ = Role.objects.get_or_create(libelle='secretaire')
        UtilisateurRole.objects.get_or_create(user=secretaire_user, role=role_sec)
        
        # === FONCTIONS ===
        fonctions = [
            'Professeur Ordinaire',
            'Professeur Associé',
            'Chef de Travaux',
            'Assistant',
            'Chargé de Cours',
        ]
        for f in fonctions:
            Fonction.objects.get_or_create(intitule=f)
        
        # Créer une filière avec chef
        created_filieres = []
        for i, f_data in enumerate(filieres_data):
            # Créer un chef pour cette filière
            chef_email = f'chef.{f_data["code"].lower()}@esforca.cd'
            chef_user, _ = User.objects.get_or_create(
                email=chef_email,
                defaults={
                    'username': f'chef_{f_data["code"].lower()}',
                    'nom': f'Chef_{f_data["code"]}',
                    'postnom': f'De la filière',
                    'prenom': f'{f_data["libelle"].split()[0]}',
                    'sexe': random.choice(['M', 'F']),
                    'tel': f'+24380000001{i}',
                    'is_staff': True,
                    'is_active': True,
                    'is_validated': True,
                }
            )
            chef_user.set_password('demo')
            chef_user.save()
            role_chef, _ = Role.objects.get_or_create(libelle='chef de filière')
            UtilisateurRole.objects.get_or_create(user=chef_user, role=role_chef)
            
            fonction = Fonction.objects.order_by('?').first()
            chef_personnel, _ = Personnel.objects.get_or_create(
                user=chef_user,
                defaults={
                    'fonction': fonction,
                    'grade': f'Professeur en {f_data["libelle"]}'
                }
            )
            
            filiere = Filiere.objects.create(
                codfiliere=f_data['code'],
                libelle=f_data['libelle'],
                descript=f'Filière {f_data["libelle"]} - Formation de qualité',
                chef=chef_personnel
            )
            created_filieres.append(filiere)
            
            # Créer quelques enseignants par filière
            for j in range(2):
                ens_email = f'enseignant.{f_data["code"].lower()}{j+1}@esforca.cd'
                ens_user, _ = User.objects.get_or_create(
                    email=ens_email,
                    defaults={
                        'username': f'ens_{f_data["code"].lower()}{j+1}',
                        'nom': f'Enseignant_{f_data["code"]}_{j+1}',
                        'postnom': f'De la filière',
                        'prenom': f'{random.choice(["Jean", "Marie", "Paul", "Sophie", "Marc", "Anne"])}',
                        'sexe': random.choice(['M', 'F']),
                        'tel': f'+2438100000{i}{j}',
                        'is_active': True,
                        'is_validated': True,
                    }
                )
                ens_user.set_password('demo')
                ens_user.save()
                role_ens, _ = Role.objects.get_or_create(libelle='enseignant')
                UtilisateurRole.objects.get_or_create(user=ens_user, role=role_ens)
                
                fonction_ens = Fonction.objects.order_by('?').first()
                Personnel.objects.get_or_create(
                    user=ens_user,
                    defaults={
                        'fonction': fonction_ens,
                        'grade': f'Assistant en {f_data["libelle"]}'
                    }
                )
            
            # Créer 20 étudiants par filière
            noms = ['Mputu', 'Kalala', 'Tshimanga', 'Mbala', 'Lubamba', 'Nkosi', 'Kazadi', 'Mwamba', 'Banza', 'Kabongo',
                    'Ilunga', 'Mutombo', 'Mbuyi', 'Tshibanda', 'Ntumba', 'Kapinga', 'Mukendi', 'Kasongo', 'Bakulu', 'Mpoyi']
            prenoms_f = ['Grace', 'Esther', 'Ruth', 'Sarah', 'Deborah', 'Naomi', 'Rachel', 'Lea', 'Judith', 'Miriam']
            prenoms_m = ['Jean', 'Paul', 'Pierre', 'Andre', 'Simon', 'David', 'Joseph', 'Samuel', 'Daniel', 'Philippe']
            
            for k in range(20):
                nom = random.choice(noms)
                prenom = random.choice(prenoms_m if k < 10 else prenoms_f)
                sexe = 'M' if k < 10 else 'F'
                email = f'etudiant.{f_data["code"].lower()}.{k+1}@esforca.cd'
                
                etudiant_user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': f'etud_{f_data["code"].lower()}_{k+1}',
                        'nom': nom,
                        'postnom': f'de {f_data["libelle"]}',
                        'prenom': prenom,
                        'sexe': sexe,
                        'tel': f'+2438200000{i}{k:02d}',
                        'adresse': f'{random.randint(1, 100)}, Avenue de l\'Université, Kinshasa',
                        'is_active': True,
                        'is_validated': True,
                    }
                )
                etudiant_user.set_password('demo')
                etudiant_user.save()
                role_etu, _ = Role.objects.get_or_create(libelle='etudiant')
                UtilisateurRole.objects.get_or_create(user=etudiant_user, role=role_etu)
                
                Etudiant.objects.get_or_create(
                    user=etudiant_user,
                    defaults={
                        'matricule': f'MAT-{f_data["code"]}-{2024}-{k+1:03d}',
                    }
                )

    def create_promotions(self):
        filieres = Filiere.objects.all()
        niveaux = ['L1', 'L2', 'L3', 'M1', 'M2']
        
        for filiere in filieres:
            for i, niveau in enumerate(niveaux):
                annee = 2024 - (len(niveaux) - 1 - i)
                promo, _ = Promotion.objects.get_or_create(
                    filiere=filiere,
                    libnom=f'{niveau} {filiere.codfiliere}',
                    defaults={
                        'annee': annee,
                        'niveau': niveau
                    }
                )
                
                # Inscrire les étudiants de cette filière dans les promotions
                etudiants = Etudiant.objects.filter(
                    user__utilisateur_roles__role__libelle='etudiant'
                )[:20]
                
                for etudiant in etudiants:
                    Inscription.objects.get_or_create(
                        etudiant=etudiant,
                        promotion=promo,
                        defaults={'annee': annee}
                    )

    def create_semestres(self):
        self.stdout.write("  📅 Création des semestres...")
        semestres_data = [
            {'libelle': 'Semestre 1', 'datedeb': '2024-09-01', 'datefin': '2025-01-31'},
            {'libelle': 'Semestre 2', 'datedeb': '2025-02-01', 'datefin': '2025-06-30'},
            {'libelle': 'Semestre 3', 'datedeb': '2024-09-01', 'datefin': '2025-01-31'},
            {'libelle': 'Semestre 4', 'datedeb': '2025-02-01', 'datefin': '2025-06-30'},
            {'libelle': 'Semestre 5', 'datedeb': '2024-09-01', 'datefin': '2025-01-31'},
            {'libelle': 'Semestre 6', 'datedeb': '2025-02-01', 'datefin': '2025-06-30'},
        ]
        for s in semestres_data:
            Semestre.objects.get_or_create(
                libsemestre=s['libelle'],
                defaults={
                    'datedeb': s['datedeb'],
                    'datefin': s['datefin']
                }
            )

    def create_cours(self):
        self.stdout.write("  📚 Création des cours...")
        matieres_par_filiere = {
            'INF': ['Algorithmique', 'Base de données', 'Programmation Web', 'Réseaux', 'Sécurité informatique',
                    'Intelligence Artificielle', 'Génie Logiciel', 'Systèmes d\'exploitation'],
            'MATH': ['Analyse', 'Algèbre', 'Statistiques', 'Probabilités', 'Géométrie',
                    'Calcul différentiel', 'Mathématiques financières', 'Topologie'],
            'PHY': ['Mécanique quantique', 'Thermodynamique', 'Électromagnétisme', 'Physique nucléaire',
                    'Optique', 'Physique des solides', 'Astrophysique', 'Mécanique des fluides'],
            'GEST': ['Comptabilité', 'Marketing', 'Ressources Humaines', 'Finance', 'Management',
                    'Droit des affaires', 'Économie', 'Entrepreneuriat'],
            'COM': ['Communication écrite', 'Journalisme', 'Relations publiques', 'Publicité',
                    'Médias numériques', 'Photographie', 'Production audiovisuelle', 'Sémiologie'],
        }
        
        semestres = Semestre.objects.all()
        for filiere in Filiere.objects.all():
            matieres = matieres_par_filiere.get(filiere.codfiliere, ['Cours général'])
            for i, matiere in enumerate(matieres):
                semestre = semestres[i % len(semestres)]
                Cours.objects.get_or_create(
                    codcours=f'{filiere.codfiliere}{i+1:03d}',
                    defaults={
                        'filiere': filiere,
                        'semestre': semestre,
                        'libelle': matiere
                    }
                )

    def create_type_evaluations(self):
        self.stdout.write("  📝 Création des types d'évaluation...")
        types = ['Examen', 'Interrogation', 'Travail Pratique', 'Projet', 'Test']
        for t in types:
            TypeEvaluation.objects.get_or_create(libelle=t)

    def create_evaluations(self):
        self.stdout.write("  📊 Création des évaluations et notes...")
        type_evals = list(TypeEvaluation.objects.all())
        
        for cours in Cours.objects.all():
            # 3 évaluations par cours
            for i in range(3):
                type_eval = type_evals[i % len(type_evals)]
                eval_instance, _ = Evaluation.objects.get_or_create(
                    cours=cours,
                    lib=f'{type_eval.libelle} {cours.libelle}',
                    defaults={
                        'type_eval': type_eval,
                        'coefficient': random.randint(1, 3),
                        'is_published': True,
                        'published_at': timezone.now(),
                    }
                )
                
                # Noter tous les étudiants inscrits dans les promotions de ce cours
                inscriptions = Inscription.objects.filter(
                    promotion__filiere=cours.filiere
                )
                for inscription in inscriptions:
                    note = round(random.uniform(5, 18), 2)
                    Cotation.objects.get_or_create(
                        etudiant=inscription.etudiant,
                        evaluation=eval_instance,
                        defaults={'note': note}
                    )