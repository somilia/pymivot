import unittest
import psycopg2
from testing.postgresql import Postgresql
from pymivot.tap.database.database_psql import Database
from pymivot.tap.features.mivot_schema import manage_mivot_schema
from pymivot.tap.exceptions.exceptions import TableAlreadyExistsException, TableDoesNotExistException


class TestManageMivotSchema(unittest.TestCase):
    def setUp(self):
        self.postgresql = Postgresql()
        self.db_params = self.postgresql.dsn()
        self.mivot = manage_mivot_schema()
        self.mivot.login_mivot_database(
            port=self.db_params['port'],
            host=self.db_params['host'],
            database=self.db_params['database'],
            user=self.db_params['user'],
            password=None
        )
        self.assertIsNotNone(self.mivot.db.connection)
        self.mivot.mivot_schema_init("mango")
        self.assertTrue(self.mivot.db._table_exists("mango", schema_name=self.mivot.schema))

    def test_mivot_add_mapped_class(self):
        self.assertEqual(self.mivot.db.fetch_data("mango", schema_name="tap_schema", columns=["instance_id"]), [])
        instance_id = self.mivot.mivot_add_mapped_class(
            "mango", "epic_src", "meas_LonLatPos",
            {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}}, "pos.main", "#POS")
        self.assertIsNotNone(
            self.mivot.db.fetch_data("mango", schema_name="tap_schema", columns=["instance_id"],
                                     condition=f"instance_id='{instance_id}'"))

        with self.assertRaises(TableAlreadyExistsException):
            self.mivot.mivot_add_mapped_class(
            "mango", "epic_src", "meas_LonLatPos",
            {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                "pos.main", "#POS", instance_id=instance_id)
            self.mivot.mivot_add_mapped_class(
                "mango", "epic_src", "meas_LonLatPos",
                {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                "pos.main", "#POS")

        self.mivot.mivot_drop_mapped_class("mango", instance_id=instance_id)
        self.assertEqual(
            self.mivot.db.fetch_data("mango", schema_name="tap_schema", columns=["instance_id"],
                                     condition=f"instance_id='{instance_id}'"), [])
        with self.assertRaises(TableDoesNotExistException):
            self.mivot.mivot_drop_mapped_class("mango", instance_id="fake_instance_id")

    def test_mivot_add_error_to_mapped_class(self):
        instance_id = self.mivot.mivot_add_mapped_class(
            "mango", "epic_src", "meas_LonLatPos",
            {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}}, "pos.main", "#POS")

        self.mivot.mivot_add_error_to_mapped_class("mango", instance_id, "error")
        self.assertIsNotNone(
            self.mivot.db.fetch_data("mango", schema_name="tap_schema", columns=["dmerror"],
                                     condition=f"instance_id='{instance_id}'"))

        self.mivot.mivot_drop_error_from_mapped_class("mango", instance_id)
        self.assertEqual(
            self.mivot.db.fetch_data("mango", schema_name="tap_schema", columns=["dmerror"],
                                     condition=f"instance_id='{instance_id}'"), [(None,)])

    def tearDown(self):
        self.mivot.logout_mivot_database()
        self.mivot.db._close_connection()
        self.postgresql.stop()
