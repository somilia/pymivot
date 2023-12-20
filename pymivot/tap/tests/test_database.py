import unittest
import psycopg2
from testing.postgresql import Postgresql
from pymivot.tap.database.database_psql import Database_psql
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.postgresql = Postgresql()
        self.db_params = self.postgresql.dsn()
        self.db = Database_psql(
            port=self.db_params['port'],
            host=self.db_params['host'],
            database=self.db_params['database'],
            user=self.db_params['user'],
            password=None
        )
        self.assertIsNotNone(self.db.connection)
        columns = """id SERIAL PRIMARY KEY, first_name TEXT, last_name TEXT"""
        self.db.create_table('first_table_test', columns)
        self.db.create_schema('first_schema_test')
        self.db.create_table('first_table_test_with_schema', columns, schema_name='first_schema_test')

    def tearDown(self):
        self.db._close_connection()
        self.postgresql.stop()

    def test_create_and_drop_table(self):
        columns = """id SERIAL PRIMARY KEY, first_name TEXT, last_name TEXT"""
        self.db._drop_table('new_table_test')
        # Test the create_table method with a non-existing mapped_table
        self.assertFalse(self.db._table_exists('new_table_test'))

        self.db.create_table('new_table_test', columns)
        self.assertTrue(self.db._table_exists('new_table_test'))

        # Test the create_table method with an existing mapped_table
        with self.assertRaises(TableAlreadyExistsException):
            self.db.create_table('new_table_test', columns)

        # Test the drop_table method with an existing mapped_table
        self.db._drop_table('new_table_test')
        self.assertFalse(self.db._table_exists('new_table_test'))

        # Test the drop_table method with a non-existing mapped_table
        # with self.assertRaises(TableDoesNotExistException):
        #     self.db._drop_table('new_table_test')

        # Test with schema
        self.db.create_table('new_table_test_with_schema', columns, schema_name='first_schema_test')
        self.assertTrue(self.db._table_exists('new_table_test_with_schema', schema_name='first_schema_test'))
        self.db._drop_table('new_table_test_with_schema', schema_name='first_schema_test')
        self.assertFalse(self.db._table_exists('new_table_test_with_schema', schema_name='first_schema_test'))

    def test_table_exists(self):
        self.assertTrue(self.db._table_exists('first_table_test'))
        self.assertFalse(self.db._table_exists('new_table_test'))
        self.db.create_table('new_table_test', 'id SERIAL PRIMARY KEY, first_name TEXT, last_name TEXT')
        # Test the table_exists method with the created mapped_table
        self.assertTrue(self.db._table_exists('new_table_test'))
        # Test the table_exists method with a non-existing mapped_table
        self.assertFalse(self.db._table_exists('public'))

        # Test the table_exists with schema
        self.db.create_schema('new_schema_test')
        self.assertFalse(self.db._table_exists('new_table_test_with_schema', schema_name='new_schema_test'))
        self.db.create_table('new_table_test_with_schema', 'id SERIAL PRIMARY KEY, first_name TEXT, last_name TEXT', schema_name='new_schema_test')
        self.assertTrue(self.db._table_exists('new_table_test_with_schema', schema_name='new_schema_test'))

    def test_insert_and_fetch_data(self):
        columns = """id SERIAL PRIMARY KEY, first_name TEXT, last_name TEXT"""
        # Test the insert_data method with an existing mapped_table
        self.db._insert_data('first_table_test', ['first_name', 'last_name'], ('John', 'Doe'))
        self.db._insert_data('first_table_test', ['first_name', 'last_name'], ('Jane', 'Doe'))
        self.db._insert_data('first_table_test', ['first_name', 'last_name'], ('John', 'Smith'))

        # Test the insert_data method with a non-existing mapped_table
        with self.assertRaises(TableDoesNotExistException):
            self.db._insert_data('table_inexistante', ['first_name', 'last_name'], ('John', 'Doe'))

        # Test the fetch_data method with an existing mapped_table
        data = self.db.fetch_data('first_table_test').data
        self.assertEqual(len(data), 3)

        # Fetch with columns
        data = self.db.fetch_data('first_table_test', columns=['first_name']).data
        self.assertEqual(len(data), 3)

        # Fetch with a condition
        data = self.db.fetch_data('first_table_test', condition="id <= 2").data
        self.assertEqual(len(data), 2)

        # Test the fetch_data method with a non-existing mapped_table
        with self.assertRaises(TableDoesNotExistException):
            self.db.fetch_data('table_inexistante').data

        # Remove a row
        self.db.remove_data('first_table_test', column_name='id', value=1)
        data = self.db.fetch_data('first_table_test').data
        self.assertEqual(len(data), 2)

        # Remove a row from a non-existing mapped_table
        with self.assertRaises(TableDoesNotExistException):
            self.db.remove_data('table_inexistante', column_name='id', value=1)

        # Test with schema
        self.db._insert_data('first_table_test_with_schema', ['first_name', 'last_name'], ('John', 'Doe'), schema_name='first_schema_test')
        self.db._insert_data('first_table_test_with_schema', ['first_name', 'last_name'], ('Jane', 'Doe'), schema_name='first_schema_test')
        self.db._insert_data('first_table_test_with_schema', ['first_name', 'last_name'], ('John', 'Smith'), schema_name='first_schema_test')
        data = self.db.fetch_data('first_table_test_with_schema', schema_name='first_schema_test').data
        self.assertEqual(len(data), 3)

    def test_insert_with_verification(self):
        self.db.insert_and_verify_data(table_name='first_table_test_with_schema', schema_name='first_schema_test', column_names=['first_name', 'last_name'], values=('Jamy', 'Ley'))
        data = self.db.fetch_data('first_table_test_with_schema', schema_name='first_schema_test').data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][1], 'Jamy')
        self.db.insert_and_verify_data(table_name='first_table_test_with_schema', schema_name='first_schema_test', column_names=['last_name', 'first_name'], values=('Ley2', 'Jamy2'))
        data = self.db.fetch_data('first_table_test_with_schema', schema_name='first_schema_test').data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1][1], 'Jamy2')
        with self.assertRaises(psycopg2.errors.NotNullViolation):
            self.db.insert_and_verify_data(table_name='first_table_test_with_schema', schema_name='first_schema_test', column_names=['first_name', 'last_name'], values=(None, 'Ley'))

if __name__ == '__main__':
    unittest.main()
