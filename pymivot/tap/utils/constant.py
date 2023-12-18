
class CONSTANT:
    TAP_SCHEMA = "tap_schema"
    COLUMNS = """
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
    COLUMNS_NAME = ["instance_id", "mapped_table", "mapped_column", "dmtype", "dmrole", "dmerror", "frame", "ucd", "vocab"]
