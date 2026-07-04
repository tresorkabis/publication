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
