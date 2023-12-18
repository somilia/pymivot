from pymivot.tap.database.database_psql import Database
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException


class manage_mivot_schema(object):

    def __init__(self):
        self.db = None
        self.schema = None
        self.columns = None

    def login_mivot_database(self, host, port, database, user, password=None):
        """
        Connect to the database
        """
        self.db = Database(host, port, database, user, password=None)
        self.schema = "tap_schema"
        self.columns = """
            instance_id TEXT NOT NULL,
            mapped_table TEXT NOT NULL,
            mapped_column TEXT NOT NULL,
            dmtype TEXT NOT NULL,
            dmrole TEXT NOT NULL,
            dmerror TEXT,
            frame TEXT,
            ucd TEXT,
            vocab TEXT
        """

    def logout_mivot_database(self):
        """
        Close the connection to the database
        """
        self.db._close_connection()

    def mivot_schema_init(self, model, with_association=False):
        """
        Create the table TAP_SCHEMA.model_mivot
        If with_association is set as True, the table TAP_SCHEMA.model_mivot_association is also created.
        An exception is risen if the table already exists
        """
        if self.db._table_exists(model, self.schema):
            raise TableAlreadyExistsException(f"The table {self.db._get_table_name(model)} already exists in the schema tap_schema.")

        self.db.create_schema("TAP_SCHEMA")
        self.db.create_table(model, self.columns, schema_name=self.schema)

        if with_association is True:
            raise NotImplemented("The association table is not implemented yet.")

    def mivot_drop_schema(self, model):
        """
        Drop the table TAP_SCHEMA.model_mivot
        Drop TAP_SCHEMA.model_mivot_association if it exists.
        """
        self.db._drop_table(model, self.schema)
        if self.db._table_exists(f"{model}_mivot_association", self.schema):
            self.db._drop_table(f"{model}_mivot_association", self.schema)

    def generate_instance_id(self, dmtype):
        """
        Generate an instance_id for the given dmtype
        """
        return f"__{dmtype}_main_"

    def get_row_by_instance_id(self, instance_id):
        """
        Return the row with the given instance_id
        """
        return self.db.fetch_data("mango", schema_name="tap_schema", columns=["instance_id"], condition=f"instance_id='{instance_id}'")

    def mivot_add_mapped_class(self, model, table, dmtype, columns, ucd=None, vocab=None, instance_id=None):
        """
        Add a mapping to a model class. This class uses the VODML file to check
        Return an auto-generated instance_id of not given as a parameter
        Rise an exception if
        - the id already exist
        - dmtype does not exist in the model
        - Some role does not exist in the model class
        - If some frame does not match the model subsetting rules

        Parameters
        ----------
        model : str
            The model name
        table : str
            The mapped table name
        dmtype : str
            The mapped column type
        column : dict
            format: {column: {dmrole, frame=None}, …}
        ucd : str, optional
            The mapped column ucd
        vocab : str, optional
            The mapped column vocab
        instance_id : str, optional
            The mapped column instance_id
        """
        if instance_id is None:
            instance_id = self.generate_instance_id(dmtype)

        if self.get_row_by_instance_id(instance_id):
            raise TableAlreadyExistsException("The given instance_id already exists in the table.")

        col = columns.keys()
        for key in col:
            column = key
            dmrole = columns[key]["dmrole"]
            frame = columns[key]["frame"]
            self.db.insert_data(
                model,
                ["instance_id", "mapped_table", "mapped_column", "dmtype", "dmrole", "frame", "ucd", "vocab"],
                (instance_id, table, column, dmtype, dmrole, frame, ucd, vocab),
                self.schema
            )

        return instance_id

    def mivot_drop_mapped_class(self, model, instance_id):
        """
        Drop a mapped class with its associations. This class uses the VODML file to check
        Return an auto-generated instance_id of not given as a parameter
        Rise an exception if instance_id does not exist in the table
        """
        if not self.get_row_by_instance_id(instance_id):
            raise TableDoesNotExistException("The given instance_id does not exist in the table.")
        self.db.remove_data(model, "instance_id", instance_id, self.schema)

    def mivot_add_error_to_mapped_class(self, model_name, instance_id, error_id):
        """
        Add an error object to the mapped class. The error mapping must have been declared before with mivot_add_mapped_class
        Rise an exception if
        - Instance_id has already an error
        - Error_id does not exist in the table
        - The error type breaks the model rules
        """
        if not self.get_row_by_instance_id(instance_id):
            raise TableDoesNotExistException("The given instance_id does not exist in the table.")
        if self.db.fetch_data(model_name, schema_name="tap_schema", columns=["dmerror"], condition=f"instance_id='{instance_id}'")[0][0] is not None:
            raise TableAlreadyExistsException("The given instance_id already has an error.")
        # TODO: check the error type
        self.db.update_data(model_name, "dmerror", error_id, f"instance_id='{instance_id}'", self.schema)

    def mivot_drop_error_from_mapped_class(self, model_name, instance_id):
        """
        Drop the error from the class instance_id if it exists
        """
        if self.get_row_by_instance_id(instance_id):
            self.db.update_data(model_name, "dmerror", "NULL", f"instance_id='{instance_id}'", self.schema)

    def mivot_add_association(self, target_instance_id, ass_instance_id):
        """
        Add ass_instance_id to the objects associated to target_instance_id in the table model_mivot_association
        Rise an exception if
        - One of the given IDs does not exist in model_mivot
        - Both IDs are the same
        - The same association already exists
        - The reverse association already exists
        """
        pass

    def mivot_drop_association(self, target_instance_id):
        """
        Drop all associations with target_instance_id
        Rise an exception if target_instance_id does not exist in model_mivot
        """
        pass

