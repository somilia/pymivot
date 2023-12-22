
class TableAlreadyExistsException(Exception):
    """
    Exception raised when a mapped_table already exists in the database.
    """
    pass


class TableDoesNotExistException(Exception):
    """
    Exception raised when a mapped_table does not exist in the database.
    """
    pass


class ColumnDoesNotExistException(Exception):
    """
    Exception raised when a column does not exist in the mapped_table.
    """
    pass


class SchemaAlreadyExistsException(Exception):
    """
    Exception raised when a tap_schema already exists in the database.
    """
    pass


class IdAlreadyExistsException(Exception):
    """
    Exception raised when an instance_id already exists in the database.
    """
    pass


class NotMatchingSchemaException(Exception):
    """
    Exception raised when the tap_schema of the mapped_table does not match the tap_schema of the database.
    """
    pass


class DmroleInvalidException(Exception):
    """
    Exception raised when the dmrole is not valid in the VODML model.
    """
    pass


class DmtypeInvalidException(Exception):
    """
    Exception raised when the dmtype is not valid in the VODML model.
    """
    pass


class FrameInvalidException(Exception):
    """
    Exception raised when the frame is not valid in the VODML model.
    """
    pass
