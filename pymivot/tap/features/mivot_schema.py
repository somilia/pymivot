from pymivot.tap.features.model_connection import ModelConnection
from pymivot.tap.utils.constant import CONSTANT
from pymivot.tap.database.databasepsql import DatabasePSQL
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException, \
    IdAlreadyExistsException, DmroleInvalidException, ColumnDoesNotExistException


class ManageMivotSchema(object):

    def __init__(self):
        self.db = None
        self.tap_schema = None
        self.columns = None
        self.model_check_mango = ModelConnection("../../validator/mivot_validator/instance_checking/vodml/mango.vo-dml.xml",
                                           "pymivot/tap/tmp_snippets")

    def login(self, dbms, host, port, database, user, password=None):
        """
        Connect to the database according to the dbms, check the tap_schema existence and set the tap_schema name.

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
            self.db = DatabasePSQL(host, port, database, user, password=None)
            if self.db.check_schema_exist(CONSTANT.TAP_SCHEMA) is True:
                self.tap_schema = CONSTANT.TAP_SCHEMA
            else:
                # TODO: add sqlite dbms
                print("The tap_schema TAP_SCHEMA does not exist in the database.")
        self.columns = CONSTANT.COLUMNS

    def logout(self):
        """
        Close the connection to the database
        """
        self.db._close_connection()

    def mivot_create_table(self, model, with_association=False):
        """
        Create the mapped_table TAP_SCHEMA.<model>_mivot
        If with_association is set as True, the mapped_table TAP_SCHEMA.model_mivot_association is also created.
        """
        self.db.create_table(model, columns=self.columns, schema_name=self.tap_schema, is_model=True)

        if with_association is True:
            raise NotImplemented("The association mapped_table is not implemented yet.")

    def mivot_drop_table(self, model):
        """
        Drop the mapped_table TAP_SCHEMA.model_mivot
        Drop TAP_SCHEMA.model_mivot_association if it exists.
        """
        self.db._drop_table(model, self.tap_schema)
        if self.db._table_exists(f"{model}_mivot_association", self.tap_schema):
            self.db._drop_table(f"{model}_mivot_association", self.tap_schema)

    def _generate_instance_id(self, dmtype):
        """
        Generate an instance_id for the given dmtype
        """
        return f"__{dmtype}_main_".replace(".", "_").replace(":", "_")

    def get_row_by_instance_id(self, model, instance_id):
        """
        Return the row with the given instance_id
        """
        return self.db.fetch_data(model, schema_name=self.tap_schema, columns=CONSTANT.COLUMNS_NAME, condition=f"instance_id='{instance_id}'", is_model=True)

    def mivot_add_mapped_class(self, model, mapped_table, dmtype, columns, ucd=None, vocab=None, instance_id=None):
        """
        Add a mapping to a model class. This class uses the VODML file to check.

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

        Raises
        ------
        IdAlreadyExistsException
            If the given instance_id already exists in the mapped_table
        FrameInvalidException
            If some frame does not match the model subsetting rules
        """
        if instance_id is None:
            instance_id = self._generate_instance_id(dmtype)
            if self.get_row_by_instance_id(model, instance_id).data:
                raise IdAlreadyExistsException("The given instance_id already exists in the mapped_table.")

        # Check if the class with this model on this table is not already mapped
        if self.db.fetch_data(model, schema_name=self.tap_schema, columns=["instance_id"], condition=f"mapped_table='{mapped_table}' AND instance_id='{instance_id}'", is_model=True).data:
            raise TableAlreadyExistsException(f"The class {instance_id} with the given mapped_table {mapped_table} is already mapped in the model {model}.")

        col = columns.keys()
        for key in col:
            column = key
            dmrole = columns[key]["dmrole"]
            frame = columns[key]["frame"]
            # Check if mandatory is present in the columns dict
            if "mandatory" not in columns[key].keys():
                mandatory = False
            else:
                mandatory = columns[key]["mandatory"]
            if self.model_check_mango.is_dmrole_valid(dmtype, dmrole) is True:
                self.db.insert_and_verify_data(
                    table_name=model,
                    schema_name=self.tap_schema,
                    column_names=CONSTANT.COLUMNS_NAME,
                    values=(instance_id, mapped_table, column, dmtype, dmrole, None, frame, ucd, vocab, mandatory),
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
        if not self.get_row_by_instance_id(model, instance_id).data:
            raise TableDoesNotExistException("The given instance_id does not exist in the mapped_table.")
        self.db.remove_data(model_name=model, column_name="instance_id", value=instance_id, schema_name=self.tap_schema)

    def get_mappeable_classes(self, model, mapped_table, columns):
        """
        Return a list of mappeable classes for the given mapped_table

        Parameters
        ----------
        model : str
            The model name
        mapped_table : str
            The mapped table name
        columns : tuple
            The columns to map

        Returns
        -------
        mappeable_classes : list
            The list of mappeable classes

        Raises
        ------
        TableDoesNotExistException
            If the given column does not exist in the mapped_table
        ColumnDoesNotExistException
            If the given column does not exist in the model_table
        """
        model_data = self.db.fetch_data(model, schema_name=CONSTANT.TAP_SCHEMA, columns=["instance_id", "mapped_column", "mandatory"])
        table_data = self.db.fetch_data(mapped_table, schema_name='public', columns=columns, is_model=False)

        # Check if the mapped_table exists in the TAP_SCHEMA.tables
        if not self.db.fetch_data("tables", schema_name=CONSTANT.TAP_SCHEMA, columns=["table_name"], condition=f"table_name='{mapped_table}'", is_model=False).data:
            raise TableDoesNotExistException(f"The given mapped_table {mapped_table} does not exist in the TAP_SCHEMA.tables.")

        mappeable_classes = []
        for elm in columns:  # First check each given column
            if elm not in model_data.get("mapped_column"):
                raise ColumnDoesNotExistException(f"The given column {elm} does not exist in the model_table {model}_mivot.")
            else:  # We look for rows with the given column: we add the class to the list
                for row in model_data.get_rows_from_element("mapped_column", elm):
                    if model_data.get_on_row(row, "instance_id") not in mappeable_classes:
                        mappeable_classes.append(model_data.get_on_row(row, "instance_id"))

        for id in mappeable_classes:  # Then we check if the class has all the mandatory columns asked in the given columns
            for row in model_data.get_rows_from_element("instance_id", id):
                print(row, model_data.get_on_row(row, "mapped_column"))
                print(mappeable_classes)
                if model_data.get_on_row(row, "mandatory") is True and model_data.get_on_row(row, "mapped_column") not in columns:
                    if model_data.get_on_row(row, "instance_id") in mappeable_classes:
                        print("For instance_id :", model_data.get_on_row(row, "instance_id"),
                              ", mandatory column :", model_data.get_on_row(row, "mapped_column"), "is missing.")
                        mappeable_classes.remove(model_data.get_on_row(row, "instance_id"))
        return mappeable_classes

    def set_mandatory(self, model, instance_id, mandatory):
        """
        Set the mandatory value of the mapped class instance_id
        Rise an exception if instance_id does not exist in the mapped_table

        Parameters
        ----------
        model : str
            The model name
        instance_id : str
            The mapped column instance_id
        mandatory : bool
            The mandatory value
        """
        if not self.get_row_by_instance_id(model, instance_id):
            raise TableDoesNotExistException("The given instance_id does not exist in the mapped_table.")
        self.db.update_data(model, "mandatory", mandatory, f"instance_id='{instance_id}'", self.tap_schema)

    def mivot_add_error_to_mapped_class(self, model, instance_id, error_id):
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
        if not self.get_row_by_instance_id(model, instance_id):
            raise TableDoesNotExistException("The given instance_id does not exist in the mapped_table.")
        if self.get_row_by_instance_id(model, instance_id).get("dmerror") is not None:
            raise TableAlreadyExistsException("The given instance_id already has an error.")
        # TODO: check the error type
        self.db.update_data(model, "dmerror", error_id, f"instance_id='{instance_id}'", self.tap_schema)

    def mivot_drop_error_from_mapped_class(self, model, instance_id):
        """
        Drop the error from the class instance_id if it exists

        Parameters
        ----------
        model_name : str
            The model name
        instance_id : str
            The mapped column instance_id
        """
        if self.get_row_by_instance_id(model, instance_id):
            self.db.update_data(model, "dmerror", "NULL", f"instance_id='{instance_id}'", self.tap_schema)

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

