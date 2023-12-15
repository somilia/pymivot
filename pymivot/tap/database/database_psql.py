import psycopg2
from psycopg2 import sql


class Database:
    def __init__(self, host, port, database, user, password):
        self.host = "localhost"
        self.port = port
        self.database = "saadmin"
        self.user = "saadmin"
        self.password = None

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
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Connection closed.")

    def _get_table_name(self, model_name):
        return f"model_{model_name}"

    def _table_exists(self, model_name, schema_name="public"):
        with self.connection.cursor() as cursor:
            try:
                query = f"SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = %s AND tablename = %s);"
                self.execute_query(query, [schema_name, self._get_table_name(model_name)])
                result = self.cursor.fetchone()
                return result[0]
            except psycopg2.Error as e:
                print("Erreur lors de la vérification de l'existence de la table:", e)
                return False

    def execute_query(self, query, values=None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            print("Query executed successfully.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def create_table(self, table_name, columns, schema_name=None):
        if self._table_exists(table_name):
            raise Exception(f"Table '{table_name}' already exists.")
        try:
            if schema_name:
                query = f"CREATE TABLE {schema_name}.{table_name} ({columns});"
            else:
                query = f"CREATE TABLE {table_name} ({columns});"
            self.execute_query(query)
            print(f"Table '{table_name}' created successfully.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def _drop_table(self, table_name):
        try:
            query = f"DROP TABLE IF EXISTS {table_name};"
            self.execute_query(query)
            print(f"Table '{table_name}' dropped successfully.")
        except psycopg2.Error as e:
            print("Error during the connection to the database:", e)

    def show_tables(self):
        try:
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
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

    def insert_data(self, table_name, column_names, values, schema_name=None):
        try:
            if schema_name:
                query = f"INSERT INTO {schema_name}.{table_name} ({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in values])});"
            else:
                query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['%s' for _ in values])});"

            self.cursor.execute(query, values)
            self.connection.commit()
            print("Data inserted successfully.")
        except psycopg2.Error as e:
            print("Error during the insertion of data: ", e)

    def remove_data(self, table_name, column_name, value, schema_name=None):
        try:
            if schema_name:
                query = f"DELETE FROM {schema_name}.{table_name} WHERE {column_name} = %s;"
            else:
                query = f"DELETE FROM {table_name} WHERE {column_name} = %s;"

            self.cursor.execute(query, [value])
            self.connection.commit()
            print("Data removed successfully.")
        except psycopg2.Error as e:
            print("Error during the removal of data: ", e)

    def fetch_data(self, table_name, columns=None, condition=None):
        try:
            columns_str = "*" if columns is None else ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table_name}"

            if condition:
                query += f" WHERE {condition}"

            self.execute_query(query)
            data = self.cursor.fetchall()
            return data

        except psycopg2.Error as e:
            print("Erreur lors de la récupération des données:", e)
            return None

    def show_data(self, data):
        if data:
            print("-----Data in the table:-----")
            for row in data:
                print(row)
        else:
            print("No data in the table.")

    def create_schema(self, schema_name):
        try:
            query = f"CREATE SCHEMA {schema_name};"
            self.cursor.execute(query)
            self.connection.commit()

            print(f"Schema '{schema_name}' built successfully.")
        except psycopg2.Error as e:
            print("Error during the creation of the schema: ", e)
