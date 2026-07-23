from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import (
    Role, UtilisateurRole, Fonction, Personnel, Etudiant,
    Filiere, Promotion, Inscription, Semestre, Cours, TypeEvaluation,
    Evaluation, Cotation, AnneeEtude, CalendrierAcademique, ProposalCoursEnseignant
)
from django.utils import timezone
import random
import string
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données de démonstration pour l\'application ESFORCA'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Génération des données de démonstration...")
        
        # Créer les rôles par défaut
        self.create_default_roles()
        
        # Créer les années d'étude LMD
        self.create_annees_etude()
        
        # Créer les filières
        self.create_filieres()
        
        # Créer les promotions
        self.create_promotions()
        
        # Créer les semestres
        self.create_semestres()
        
        # Créer les cours avec années et crédits
        self.create_cours()
        
        # Créer les types d'évaluation
        self.create_type_evaluations()
        
        # Créer le calendrier académique LMD
        self.create_calendrier_academique()
        
        # Créer les évaluations
        self.create_evaluations()
        
        # Quelques propositions de cours
        self.create_propositions_cours()
        
        self.stdout.write(self.style.SUCCESS("✅ Données de démonstration générées avec succès!"))
        
    def create_annees_etude(self):
        self.stdout.write("  🎓 Création des années d'étude LMD...")
        AnneeEtude.objects.get_or_create(code='L1', defaults={'libelle': 'Licence 1', 'ordre': 1})
        AnneeEtude.objects.get_or_create(code='L2', defaults={'libelle': 'Licence 2', 'ordre': 2})
        AnneeEtude.objects.get_or_create(code='L3', defaults={'libelle': 'Licence 3', 'ordre': 3})

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
        postnoms = ['Mukendi', 'Kabasele', 'Kabila', 'Lumumba', 'Mabiala', 'Tshisekedi', 'Kavumba', 'Mutombo', 'Nkongolo', 'Mbuyi']
        
        for i, f_data in enumerate(filieres_data):
            # Créer un chef pour cette filière
            chef_email = f'chef.{f_data["code"].lower()}@esforca.cd'
            chef_user, _ = User.objects.get_or_create(
                email=chef_email,
                defaults={
                    'username': f'chef_{f_data["code"].lower()}',
                    'nom': f'Chef_{f_data["code"]}',
                    'postnom': random.choice(postnoms),
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
                code=f_data['code'],
                libelle=f_data['libelle'],
                description=f'Filière {f_data["libelle"]} - Formation de qualité',
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
                        'postnom': random.choice(postnoms),
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
                        'postnom': random.choice(postnoms),
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

        # Créer d'abord toutes les promotions
        for filiere in filieres:
            for i, niveau in enumerate(niveaux):
                annee = 2024 - (len(niveaux) - 1 - i)
                Promotion.objects.get_or_create(
                    filiere=filiere,
                    libelle=f'{niveau} {filiere.code}'
                )

        # Ensuite, inscrire les étudiants avec une répartition réaliste
        for filiere in filieres:
            # Récupérer tous les étudiants de cette filière
            etudiants = list(Etudiant.objects.filter(
                user__utilisateur_roles__role__libelle='etudiant',
                matricule__startswith=f'MAT-{filiere.code}-'
            ).order_by('matricule'))

            # Répartir les étudiants entre les différents niveaux
            # L1: étudiants 0-6 (7 étudiants)
            # L2: étudiants 7-13 (7 étudiants)
            # L3: étudiants 14-20 (7 étudiants)
            # M1 et M2: pas d'étudiants pour l'instant (cycle master non implémenté)

            # Étudiants de L1 (uniquement inscription L1)
            l1_students = etudiants[:7]
            l1_promo = Promotion.objects.get(filiere=filiere, libelle=f'L1 {filiere.code}')
            for etudiant in l1_students:
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l1_promo,
                    defaults={'annee': '2024-2025'}
                )

            # Étudiants de L2 (inscriptions L1 et L2)
            l2_students = etudiants[7:14]
            l2_promo = Promotion.objects.get(filiere=filiere, libelle=f'L2 {filiere.code}')
            for etudiant in l2_students:
                # Inscription L1 (année précédente)
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l1_promo,
                    defaults={'annee': '2023-2024'}
                )
                # Inscription L2 (année actuelle)
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l2_promo,
                    defaults={'annee': '2024-2025'}
                )

            # Étudiants de L3 (inscriptions L1, L2 et L3)
            l3_students = etudiants[14:21]
            l3_promo = Promotion.objects.get(filiere=filiere, libelle=f'L3 {filiere.code}')
            for etudiant in l3_students:
                # Inscription L1
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l1_promo,
                    defaults={'annee': '2022-2023'}
                )
                # Inscription L2
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l2_promo,
                    defaults={'annee': '2023-2024'}
                )
                # Inscription L3 (année actuelle)
                Inscription.objects.get_or_create(
                    etudiant=etudiant,
                    promotion=l3_promo,
                    defaults={'annee': '2024-2025'}
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
                libelle=s['libelle']
            )

    def create_cours(self):
        self.stdout.write("  📚 Création des cours avec années LMD et crédits...")
        annees = {a.code: a for a in AnneeEtude.objects.all()}
        
        matieres_par_filiere = {
            'INF': {
                'L1': [('Algorithmique', 5), ('Base de données', 5), ('Programmation Web', 4), ('Introduction aux réseaux', 4)],
                'L2': [('Réseaux avancés', 5), ('Sécurité informatique', 5), ('Systèmes d\'exploitation', 4), ('Génie Logiciel', 4)],
                'L3': [('Intelligence Artificielle', 6), ('Data Science', 5), ('Cloud Computing', 5), ('Projet de fin d\'études', 8)],
            },
            'MATH': {
                'L1': [('Analyse 1', 5), ('Algèbre 1', 5), ('Statistiques', 4), ('Géométrie', 4)],
                'L2': [('Analyse 2', 5), ('Algèbre 2', 5), ('Probabilités', 4), ('Calcul différentiel', 4)],
                'L3': [('Mathématiques financières', 5), ('Topologie', 5), ('Analyse numérique', 5), ('Projet', 8)],
            },
            'PHY': {
                'L1': [('Mécanique', 5), ('Thermodynamique', 5), ('Électromagnétisme', 4), ('Optique', 4)],
                'L2': [('Mécanique quantique', 5), ('Physique nucléaire', 5), ('Physique des solides', 4), ('Astrophysique', 4)],
                'L3': [('Physique des particules', 5), ('Mécanique des fluides', 5), ('Physique statistique', 5), ('Projet', 8)],
            },
            'GEST': {
                'L1': [('Comptabilité', 5), ('Marketing', 5), ('Économie', 4), ('Management', 4)],
                'L2': [('Ressources Humaines', 5), ('Finance', 5), ('Droit des affaires', 4), ('Entrepreneuriat', 4)],
                'L3': [('Stratégie d\'entreprise', 5), ('Audit', 5), ('Gestion de projet', 5), ('Projet', 8)],
            },
        }
        
        semestres = list(Semestre.objects.all())
        for filiere in Filiere.objects.all():
            matieres_par_annee = matieres_par_filiere.get(filiere.code, {})
            if not matieres_par_annee:
                continue
                
            for annee_code, matieres in matieres_par_annee.items():
                annee = annees.get(annee_code)
                if not annee:
                    continue
                for i, (matiere, credit) in enumerate(matieres):
                    semestre = semestres[i % len(semestres)]
                    Cours.objects.get_or_create(
                        code=f'{filiere.code}{annee_code}{i+1:02d}',
                        defaults={
                            'filiere': filiere,
                            'semestre': semestre,
                            'annee_etude': annee,
                            'libelle': matiere,
                            'volume_horaire': random.randint(30, 60),
                            'credit': credit,
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
                    type_evaluation=type_eval,
                    cours=cours,
                    date=f'2024-{random.randint(1, 12)}-{random.randint(1, 28)}',
                    defaults={}
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

    def create_calendrier_academique(self):
        self.stdout.write("  📅 Création du calendrier académique LMD...")
        semestres = {s.libelle: s for s in Semestre.objects.all()}
        annees = {a.code: a for a in AnneeEtude.objects.all()}
        
        for filiere in Filiere.objects.all():
            promotions = Promotion.objects.filter(filiere=filiere)
            for promo in promotions:
                # Déterminer l'année d'étude à partir du libellé de la promotion
                annee_code = None
                for code in ['L1', 'L2', 'L3']:
                    if code in promo.libelle:
                        annee_code = code
                        break
                annee_etude = annees.get(annee_code) if annee_code else None
                
                # Périodes pour chaque promotion
                periodes = [
                    {
                        'type': 'S1',
                        'semestre': semestres.get('Semestre 1'),
                        'intitule': f'Session 1er semestre - {promo.libelle}',
                        'debut': date(2024, 12, 1),
                        'fin': date(2025, 1, 15),
                    },
                    {
                        'type': 'RATTRAPAGE_S1',
                        'semestre': semestres.get('Semestre 1'),
                        'intitule': f'Rattrapage 1er semestre - {promo.libelle}',
                        'debut': date(2025, 2, 1),
                        'fin': date(2025, 2, 15),
                    },
                    {
                        'type': 'S2',
                        'semestre': semestres.get('Semestre 2'),
                        'intitule': f'Session 2ème semestre - {promo.libelle}',
                        'debut': date(2025, 5, 15),
                        'fin': date(2025, 6, 30),
                    },
                    {
                        'type': 'RATTRAPAGE_S2',
                        'semestre': semestres.get('Semestre 2'),
                        'intitule': f'Rattrapage 2ème semestre - {promo.libelle}',
                        'debut': date(2025, 7, 15),
                        'fin': date(2025, 7, 30),
                    },
                ]
                
                # Rattrapage de crédits pour L2 et L3
                if annee_code in ['L2', 'L3']:
                    periodes.append({
                        'type': 'RATTRAPAGE_CREDITS',
                        'semestre': semestres.get('Semestre 1'),
                        'intitule': f'Rattrapage de crédits - {promo.libelle}',
                        'debut': date(2025, 8, 1),
                        'fin': date(2025, 8, 31),
                    })
                
                for p in periodes:
                    if p['semestre']:
                        CalendrierAcademique.objects.get_or_create(
                            filiere=filiere,
                            promotion=promo,
                            semestre=p['semestre'],
                            type_periode=p['type'],
                            annee_academique='2024-2025',
                            defaults={
                                'annee_etude': annee_etude,
                                'intitule': p['intitule'],
                                'date_debut': p['debut'],
                                'date_fin': p['fin'],
                                'est_actif': True,
                            }
                        )

    def create_propositions_cours(self):
        self.stdout.write("  📝 Création de propositions de cours...")
        enseignants = Personnel.objects.filter(
            user__utilisateur_roles__role__libelle='enseignant'
        )
        cours_list = list(Cours.objects.all())
        
        for _ in range(5):
            if cours_list and enseignants:
                cours = random.choice(cours_list)
                enseignant = random.choice(enseignants)
                ProposalCoursEnseignant.objects.get_or_create(
                    cours=cours,
                    enseignant=enseignant,
                    defaults={
                        'message': f'Proposition pour le cours de {cours.libelle}',
                        'est_accepte': random.choice([True, False]),
                    }
                )
