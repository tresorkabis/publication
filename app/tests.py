from django.db import connection
from django.test import TestCase


class UserValidationSchemaTest(TestCase):
    def test_is_validated_column_exists(self):
        with connection.cursor() as cursor:
            columns = {row[0] for row in connection.introspection.get_table_description(cursor, 'results_user')}

        self.assertIn('is_validated', columns)
