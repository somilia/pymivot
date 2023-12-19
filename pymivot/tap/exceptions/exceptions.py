
class TableAlreadyExistsException(Exception):
    """
    Exception raised when a mapped_table already exists in the database.
    """
    pass


class SchemaAlreadyExistsException(Exception):
    """
    Exception raised when a schema already exists in the database.
    """
    pass


class TableDoesNotExistException(Exception):
    """
    Exception raised when a mapped_table does not exist in the database.
    """
    pass
