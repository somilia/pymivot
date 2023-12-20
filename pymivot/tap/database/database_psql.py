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

    def _get_table_name(self, model_name, is_model=True):
        if is_model:
            return f"{model_name}_mivot"
        else:
            return f"{model_name}"

    def _table_exists(self, model_name, schema_name="public", is_model=True):
        """
        Check if a mapped_table exists in the database.
        """
        with self.connection.cursor() as cursor:
            try:
                query = f"SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = '{schema_name}' AND tablename = '{self._get_table_name(model_name, is_model)}');"
                self.cursor.execute(query)
                self.connection.commit()
                result = self.cursor.fetchone()
                return result[0]
            except psycopg2.Error as e:
                print("Erreur lors de la vérification de l'existence de la mapped_table:", e)
                return False

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def create_table(self, model_name, columns, schema_name='public', is_model=True):
        if self._table_exists(model_name, schema_name):
            raise TableAlreadyExistsException(f'Table "{schema_name}".{self._get_table_name(model_name, is_model)} already exists.')
        try:
            query = f'CREATE TABLE "{schema_name}"."{self._get_table_name(model_name, is_model)}" ({columns});'
            self.execute_query(query)
            print(f'Table "{schema_name}".{self._get_table_name(model_name, is_model)} created successfully.')
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def _drop_table(self, model_name, schema_name="public"):
        try:
            query = f'DROP TABLE IF EXISTS "{schema_name}".{self._get_table_name(model_name)} CASCADE;'
            self.execute_query(query)
            print(f'Table "{schema_name}".{self._get_table_name(model_name)} dropped successfully.')
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
                columns = [desc[0] for desc in self.cursor.description]
                return DataWrapper(tables, columns)
            else:
                print("No tables in the database.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def _insert_data(self, model_name, column_names, values, schema_name='public', is_model=True):
        if not self._table_exists(model_name, schema_name, is_model=is_model):
            raise TableDoesNotExistException(f"Table {schema_name}.{self._get_table_name(model_name, is_model)} does not exists.")
        try:
            query = (f'INSERT INTO "{schema_name}".{self._get_table_name(model_name, is_model)} '
                     f"({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in values])});")

            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Data inserted in {schema_name}.{self._get_table_name(model_name, is_model)} successfully.")
        except psycopg2.Error as e:
            print("Error during the insertion of data: ", e)

    def insert_and_verify_data(self, table_name, schema_name, column_names, values, is_model=True):
        # Check if table exists
        if not self._table_exists(table_name, schema_name, is_model=is_model):
            raise Exception(f"Table {schema_name}.{self._get_table_name(table_name, is_model)} does not exist.")

        # Get table schema
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema_name}' AND table_name = '{self._get_table_name(table_name, is_model)}';"
        self.cursor.execute(query)
        table_schema = self.cursor.fetchall()
        print(" --- Table Schema :", table_schema)

        # Check if provided column names match with table schema
        schema_column_names = [column[0] for column in table_schema]
        # if set(column_names) != set(schema_column_names):
        if not set(column_names).issubset(set(schema_column_names)):
            raise Exception("Provided column names do not match with table schema.")

        # Insert data into table
        self._insert_data(table_name, column_names, values, schema_name, is_model=is_model)

        # Fetch data from table to verify insertion
        fetched_data = self.fetch_data(model_name=table_name, schema_name=schema_name, columns=column_names, is_model=is_model)
        if values not in fetched_data.data:
            print(" --- Fetched data :", fetched_data.data)
            print(" --- Values :", values)
            raise Exception("Data verification failed after insertion.")

    def remove_data(self, model_name, column_name, value, schema_name='public', is_model=True):
        if not self._table_exists(model_name, schema_name, is_model=is_model):
            raise TableDoesNotExistException(f"Table {schema_name}.{self._get_table_name(model_name, is_model)} does not exists.")
        try:
            query = (f'DELETE FROM "{schema_name}".{self._get_table_name(model_name, is_model)} WHERE {column_name} = '
                    f"'{value}';")

            self.cursor.execute(query)
            self.connection.commit()
            print(f"Data where {column_name} = {value} removed successfully in {schema_name}.{self._get_table_name(model_name, is_model)}.")
        except psycopg2.Error as e:
            print("Error during the removal of data: ", e)

    def update_data(self, model_name, column_name, value, condition, schema_name='public', is_model=True):
        if not self._table_exists(model_name, schema_name, is_model=is_model):
            raise TableDoesNotExistException(f'Table "{schema_name}".{self._get_table_name(model_name, is_model)} does not exists.')
        try:
            if value == "NULL":
                query = f'UPDATE "{schema_name}".{self._get_table_name(model_name, is_model)} SET {column_name} = NULL WHERE {condition};'
            else:
                query = (f'UPDATE "{schema_name}".{self._get_table_name(model_name, is_model)} SET {column_name} = '
                         f"'{value}' WHERE {condition};")

            self.cursor.execute(query)
            self.connection.commit()
            print(f'Data updated in "{schema_name}".{self._get_table_name(model_name, is_model)} successfully.')
        except psycopg2.Error as e:
            print("Error during the update of data: ", e)

    def fetch_data(self, model_name, schema_name='public', columns=None, condition=None, is_model=True):
        if not self._table_exists(model_name, schema_name=schema_name, is_model=is_model):
            raise TableDoesNotExistException(f'Table "{schema_name}".{self._get_table_name(model_name, is_model)} does not exists.')
        try:
            columns_str = "*" if columns is None else ", ".join(columns)
            query = f'SELECT {columns_str} FROM "{schema_name}".{self._get_table_name(model_name, is_model)}'

            if condition:
                query += f" WHERE {condition}"
            self.execute_query(query)
            data = self.cursor.fetchall()
            if columns is None:
                columns = [desc[0] for desc in self.cursor.description]
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
        if self.check_schema_exist(schema_name):
            raise exceptions.SchemaAlreadyExistsException(f'Schema "{schema_name}" already exists.')
        try:
            query = f'CREATE SCHEMA "{schema_name}";'
            self.cursor.execute(query)
            self.connection.commit()

            print(f'Schema "{schema_name}" built successfully.')
        except psycopg2.Error as e:
            print("Error during the creation of the schema: ", e)

    def drop_schema(self, schema_name):
        try:
            query = f"DROP SCHEMA IF EXISTS '{schema_name}' CASCADE;"
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
