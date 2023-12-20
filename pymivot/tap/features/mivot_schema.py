from pymivot.tap.utils.constant import CONSTANT
from pymivot.tap.database.database_psql import Database_psql
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException


class ManageMivotSchema(object):

    def __init__(self):
        self.db = None
        self.schema = None
        self.columns = None

    def login(self, dbms, host, port, database, user, password=None):
        """
        Connect to the database according to the dbms and check the schema existence.

        Parameters
        ----------
        dbms : str
            The database management system name
        host : str
            The database host
        port : str
            The database port
        database : str
            The database name
        user : str
            The database user
        password : str, optional
            The database password
        """
        if dbms == CONSTANT.PSQL:
            self.db = Database_psql(host, port, database, user, password=None)
            if self.db.check_schema_exist(CONSTANT.TAP_SCHEMA) is True:
                self.schema = CONSTANT.TAP_SCHEMA
            else:
                # TODO: add sqlite dbms
                print("The schema TAP_SCHEMA does not exist in the database.")
        self.columns = CONSTANT.COLUMNS

    def logout(self):
        """
        Close the connection to the database
        """
        self.db._close_connection()

    def mivot_create_table(self, model, with_association=False):
        """
        Create the mapped_table TAP_SCHEMA.model_mivot
        If with_association is set as True, the mapped_table TAP_SCHEMA.model_mivot_association is also created.
        An exception is risen if the mapped_table already exists
        """
        if self.db._table_exists(model, self.schema):
            raise TableAlreadyExistsException(f"The mapped_table {self.db._get_table_name(model)} already exists in the schema tap_schema.")

        self.db.create_table(model, self.columns, schema_name=self.schema)

        if with_association is True:
            raise NotImplemented("The association mapped_table is not implemented yet.")

    def mivot_drop_table(self, model):
        """
        Drop the mapped_table TAP_SCHEMA.model_mivot
        Drop TAP_SCHEMA.model_mivot_association if it exists.
        """
        self.db._drop_table(model, self.schema)
        if self.db._table_exists(f"{model}_mivot_association", self.schema):
            self.db._drop_table(f"{model}_mivot_association", self.schema)

    def _generate_instance_id(self, dmtype):
        """
        Generate an instance_id for the given dmtype
        """
        return f"__{dmtype}_main_".replace(".", "_").replace(":", "_")

    def get_row_by_instance_id(self, instance_id):
        """
        Return the row with the given instance_id
        """
        return self.db.fetch_data("mango", schema_name=self.schema, columns=CONSTANT.COLUMNS_NAME, condition=f"instance_id='{instance_id}'", is_model=True)

    def mivot_add_mapped_class(self, model, mapped_table, dmtype, columns, ucd=None, vocab=None, instance_id=None):
        """
        Add a mapping to a model class. This class uses the VODML file to check.
        Rise an exception if:
        - the id already exist
        - dmtype does not exist in the model
        - Some role does not exist in the model class
        - If some frame does not match the model subsetting rules

        Parameters
        ----------
        model : str
            The model name
        mapped_table : str["instance_id"]
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

        Returns
        -------
        instance_id : str
            The mapped column instance_id
        """
        if instance_id is None:
            instance_id = self._generate_instance_id(dmtype)

        if self.get_row_by_instance_id(instance_id).data:
            raise TableAlreadyExistsException("The given instance_id already exists in the mapped_table.")

        col = columns.keys()
        for key in col:
            column = key
            dmrole = columns[key]["dmrole"]
            frame = columns[key]["frame"]
            self.db.insert_and_verify_data(
                table_name=model,
                schema_name=self.schema,
                column_names=CONSTANT.COLUMNS_NAME,
                values=(instance_id, mapped_table, column, dmtype, dmrole, None, frame, ucd, vocab),
                is_model=True
            )

        return instance_id

    def mivot_drop_mapped_class(self, model, instance_id):
        """
        Drop a mapped class with its associations. This class uses the VODML file to check
        Return an auto-generated instance_id of not given as a parameter
        Rise an exception if instance_id does not exist in the mapped_table

        Parameters
        ----------
        model : str
            The model name
        instance_id : str
            The mapped column instance_id
        """
        if not self.get_row_by_instance_id(instance_id).data:
            raise TableDoesNotExistException("The given instance_id does not exist in the mapped_table.")
        self.db.remove_data(model_name=model, column_name="instance_id", value=instance_id, schema_name=self.schema)

    def mivot_add_error_to_mapped_class(self, model_name, instance_id, error_id):
        """
        Add an error object to the mapped class. The error mapping must have been declared before with mivot_add_mapped_class.
        Rise an exception if:
        - Instance_id has already an error
        - Error_id does not exist in the mapped_table
        - The error type breaks the model rules

        Parameters
        ----------
        model_name : str
            The model name
        instance_id : str
            The mapped column instance_id
        error_id : str
            The error id

        Raises
        ------
        TableDoesNotExistException
            If instance_id does not exist in the mapped_table
        TableAlreadyExistsException
            If instance_id already has an error
        """
        if not self.get_row_by_instance_id(instance_id):
            raise TableDoesNotExistException("The given instance_id does not exist in the mapped_table.")
        if self.get_row_by_instance_id(instance_id).get("dmerror") is not None:
            raise TableAlreadyExistsException("The given instance_id already has an error.")
        # TODO: check the error type
        self.db.update_data(model_name, "dmerror", error_id, f"instance_id='{instance_id}'", self.schema)

    def mivot_drop_error_from_mapped_class(self, model_name, instance_id):
        """
        Drop the error from the class instance_id if it exists

        Parameters
        ----------
        model_name : str
            The model name
        instance_id : str
            The mapped column instance_id
        """
        if self.get_row_by_instance_id(instance_id):
            self.db.update_data(model_name, "dmerror", "NULL", f"instance_id='{instance_id}'", self.schema)

    def mivot_add_association(self, target_instance_id, ass_instance_id):
        """
        Add ass_instance_id to the objects associated to target_instance_id in the mapped_table model_mivot_association
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

