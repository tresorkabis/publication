from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase


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
