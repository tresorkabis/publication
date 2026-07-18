from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from app.models import (
    Cotation,
    Cours,
    Etudiant,
    Evaluation,
    Filiere,
    Inscription,
    Personnel,
    Promotion,
    ProposalCoursEnseignant,
    Role,
    Semestre,
    TypeEvaluation,
    UtilisateurRole,
)


class UserValidationSchemaTest(TestCase):
    def test_is_validated_column_exists(self):
        with connection.cursor() as cursor:
            columns = {row[0] for row in connection.introspection.get_table_description(cursor, 'results_user')}

        self.assertIn('is_validated', columns)


class DashboardAccessTest(TestCase):
    def test_dashboard_renders_for_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='secretaire_test',
            email='secretaire_test@example.com',
            password='demo',
            is_staff=True,
            is_active=True,
            is_validated=True,
        )

        self.client.force_login(user)
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_chef_dashboard_shows_filiere_metrics(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='chef_test',
            email='chef_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        personnel = Personnel.objects.create(user=user, grade='Chef de filière')
        role = Role.objects.get_or_create(libelle='chef de filière')[0]
        UtilisateurRole.objects.get_or_create(user=user, role=role)

        filiere = Filiere.objects.create(code='INF', libelle='Informatique', chef=personnel)
        semestre = Semestre.objects.create(libelle='S1')
        cours = Cours.objects.create(filiere=filiere, semestre=semestre, code='INF101', libelle='Algorithmique', volume_horaire=30)
        promotion = Promotion.objects.create(filiere=filiere, libelle='L1')
        type_evaluation = TypeEvaluation.objects.create(libelle='Devoir')
        evaluation = Evaluation.objects.create(type_evaluation=type_evaluation, cours=cours, date='2026-01-01', is_published=True)

        student_user = User.objects.create_user(
            username='student_test',
            email='student_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        student = Etudiant.objects.create(user=student_user, matricule='MAT-TEST-002')
        Inscription.objects.create(etudiant=student, promotion=promotion, annee='2025-2026')
        Cotation.objects.create(etudiant=student, evaluation=evaluation, note='14.25')

        self.client.force_login(user)
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ma filière')
        self.assertContains(response, 'Informatique')
        self.assertContains(response, 'Étudiants')
        self.assertContains(response, 'Algorithmique')
        self.assertNotContains(response, 'Utilisateurs Totaux')

    def test_student_dashboard_shows_own_marks(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='etudiant_test',
            email='etudiant_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        etudiant = Etudiant.objects.create(user=user, matricule='MAT-TEST-001')

        filiere = Filiere.objects.create(code='INF', libelle='Informatique')
        semestre = Semestre.objects.create(libelle='S1')
        cours = Cours.objects.create(filiere=filiere, semestre=semestre, code='INF101', libelle='Algorithmique', volume_horaire=30)
        type_evaluation = TypeEvaluation.objects.create(libelle='Devoir')
        evaluation = Evaluation.objects.create(type_evaluation=type_evaluation, cours=cours, date='2026-01-01', is_published=True)
        Cotation.objects.create(etudiant=etudiant, evaluation=evaluation, note='15.50')

        self.client.force_login(user)
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Algorithmique')
        self.assertContains(response, '15.50')
        self.assertNotContains(response, 'Utilisateurs Totaux')
        self.assertNotContains(response, 'Répartition Étudiants par Promotion')

    def test_chef_can_plan_an_exam(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='chef_plan_test',
            email='chef_plan_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        personnel = Personnel.objects.create(user=user, grade='Chef de filière')
        role = Role.objects.get_or_create(libelle='chef de filière')[0]
        UtilisateurRole.objects.get_or_create(user=user, role=role)

        filiere = Filiere.objects.create(code='INF', libelle='Informatique', chef=personnel)
        semestre = Semestre.objects.create(libelle='S1')
        cours = Cours.objects.create(filiere=filiere, semestre=semestre, code='INF102', libelle='Bases de données', volume_horaire=30)
        type_evaluation = TypeEvaluation.objects.create(libelle='Examen')

        self.client.force_login(user)
        response = self.client.get('/resultats/planifier-examen/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Planifier un examen')

        response = self.client.post('/resultats/planifier-examen/', {
            'type_evaluation': type_evaluation.id,
            'cours': cours.id,
            'date': '2026-03-10',
            'coefficient': '2',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Evaluation.objects.filter(cours=cours, date='2026-03-10').exists())

    def test_chef_can_propose_course_to_teacher(self):
        User = get_user_model()
        chef_user = User.objects.create_user(
            username='chef_proposition_test',
            email='chef_proposition_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        chef_personnel = Personnel.objects.create(user=chef_user, grade='Chef de filière')
        role_chef = Role.objects.get_or_create(libelle='chef de filière')[0]
        UtilisateurRole.objects.get_or_create(user=chef_user, role=role_chef)

        teacher_user = User.objects.create_user(
            username='enseignant_test',
            email='enseignant_test@example.com',
            password='demo',
            is_active=True,
            is_validated=True,
        )
        teacher_personnel = Personnel.objects.create(user=teacher_user, grade='Enseignant')
        role_enseignant = Role.objects.get_or_create(libelle='enseignant')[0]
        UtilisateurRole.objects.get_or_create(user=teacher_user, role=role_enseignant)

        filiere = Filiere.objects.create(code='INF', libelle='Informatique', chef=chef_personnel)
        semestre = Semestre.objects.create(libelle='S1')
        cours = Cours.objects.create(filiere=filiere, semestre=semestre, code='INF103', libelle='Programmation', volume_horaire=45)

        self.client.force_login(chef_user)
        response = self.client.get('/resultats/proposer-cours/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proposer un cours')

        response = self.client.post('/resultats/proposer-cours/', {
            'cours': cours.id,
            'enseignant': teacher_personnel.id,
            'message': 'Ce cours est proposé pour cet enseignant.',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProposalCoursEnseignant.objects.filter(cours=cours, enseignant=teacher_personnel).exists())
