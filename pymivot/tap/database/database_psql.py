import psycopg2
from psycopg2 import sql
from pymivot.tap import exceptions
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException
from pymivot.tap.features.data_wrapper import DataWrapper


class Database_psql:
    """
    Class used to connect to a PostgreSQL database and execute queries.
    """
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        try:
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            self.cursor = self.connection.cursor()
            print("Connection to the database successful.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def _close_connection(self):
        """
        Close the connection to the database.
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Connection closed.")

    def _get_table_name(self, model_name):
        return f"{model_name}_mivot"

    def _table_exists(self, model_name, schema_name="public"):
        """
        Check if a mapped_table exists in the database.
        """
        table_name = self._get_table_name(model_name)
        with self.connection.cursor() as cursor:
            try:
                query = "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = '"+schema_name+"' AND tablename = '"+table_name+"');"
                self.execute_query(query)
                result = self.cursor.fetchone()
                return result[0]
            except psycopg2.Error as e:
                print("Erreur lors de la vérification de l'existence de la mapped_table:", e)
                return False

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Query executed successfully.")
            return self.cursor
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def create_table(self, model_name, columns, schema_name='public'):
        table_name = self._get_table_name(model_name)
        if self._table_exists(model_name, schema_name):
            raise TableAlreadyExistsException(f"Table {schema_name}.{table_name} already exists.")
        try:
            query = f"CREATE TABLE {schema_name}.{table_name} ({columns});"
            self.execute_query(query)
            print(f"Table {schema_name}.{table_name} created successfully.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def _drop_table(self, model_name, schema_name="public"):
        try:
            query = f"DROP TABLE IF EXISTS {schema_name}.{self._get_table_name(model_name)} CASCADE;"
            self.execute_query(query)
            print(f"Table '{schema_name}.{self._get_table_name(model_name)}' dropped successfully.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def show_tables(self, schema_name='public'):
        try:
            query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';"
            self.execute_query(query)
            tables = self.cursor.fetchall()

            if tables:
                print("-----Tables in the database:-----")
                for table in tables:
                    print(table[0])
            else:
                print("No tables in the database.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def insert_data(self, model_name, column_names, values, schema_name='public'):
        if not self._table_exists(model_name, schema_name):
            raise TableDoesNotExistException(f"Table {schema_name}.{self._get_table_name(model_name)} does not exists.")
        try:
            query = (f"INSERT INTO {schema_name}.{self._get_table_name(model_name)} "
                     f"({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in values])});")

            self.cursor.execute(query, values)
            self.connection.commit()
            print("Data inserted successfully.")
        except psycopg2.Error as e:
            print("Error during the insertion of data: ", e)

    def remove_data(self, model_name, column_name, value, schema_name='public'):
        if not self._table_exists(model_name, schema_name):
            raise TableDoesNotExistException(f"Table {schema_name}.{self._get_table_name(model_name)} does not exists.")
        try:
            query = f"DELETE FROM {schema_name}.{self._get_table_name(model_name)} WHERE {column_name} = %s;"

            self.cursor.execute(query, [value])
            self.connection.commit()
            print("Data removed successfully.")
        except psycopg2.Error as e:
            print("Error during the removal of data: ", e)

    def update_data(self, model_name, column_name, value, condition, schema_name='public'):
        if not self._table_exists(model_name, schema_name):
            raise TableDoesNotExistException(f"Table {schema_name}.{self._get_table_name(model_name)} does not exists.")
        try:
            if value == "NULL":
                query = f"UPDATE {schema_name}.{self._get_table_name(model_name)} SET {column_name} = NULL WHERE {condition};"
            else:
                query = f"UPDATE {schema_name}.{self._get_table_name(model_name)} SET {column_name} = '{value}' WHERE {condition};"

            self.cursor.execute(query)
            self.connection.commit()
            print("Data updated successfully.")
        except psycopg2.Error as e:
            print("Error during the update of data: ", e)

    def fetch_data(self, model_name, schema_name='public', columns=None, condition=None):
        table_name = self._get_table_name(model_name)
        if not self._table_exists(model_name, schema_name):
            raise TableDoesNotExistException(f"Table {schema_name}.{table_name} does not exists.")
        try:
            columns_str = "*" if columns is None else ", ".join(columns)
            query = f"SELECT {columns_str} FROM {schema_name}.{table_name}"

            if condition:
                query += f" WHERE {condition}"

            self.execute_query(query)
            data = self.cursor.fetchall()
            return DataWrapper(data, columns)

        except psycopg2.Error as e:
            print("Erreur lors de la récupération des données:", e)
            return None

    def show_data(self, data):
        if data:
            print("-----Data in the mapped_table:-----")
            for row in data:
                print(row)
        else:
            print("No data in the mapped_table.")

    def create_schema(self, schema_name):
        try:
            query = f"CREATE SCHEMA {schema_name};"
            self.cursor.execute(query)
            self.connection.commit()

            print(f"Schema '{schema_name}' built successfully.")
        except psycopg2.Error as e:
            print("Error during the creation of the schema: ", e)

    def drop_schema(self, schema_name):
        try:
            query = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"
            self.cursor.execute(query)
            self.connection.commit()

            print(f"Schema '{schema_name}' dropped successfully.")
        except psycopg2.Error as e:
            print("Error during the drop of the schema: ", e)

    def check_schema_exist(self, schema_name):
        try:
            query = f"SELECT EXISTS (SELECT FROM pg_catalog.pg_namespace WHERE nspname = '{schema_name}');"
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0]
        except psycopg2.Error as e:
            print("Error during the check of the schema existence:", e)
            return False
