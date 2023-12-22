import unittest
import psycopg2
from testing.postgresql import Postgresql
from pymivot.tap.database.databasepsql import DatabasePSQL
from pymivot.tap.features.mivot_schema import ManageMivotSchema
from pymivot.tap.exceptions.exceptions import (TableAlreadyExistsException,
                                               TableDoesNotExistException,
                                               DmroleInvalidException,
                                               DmtypeInvalidException,
                                               IdAlreadyExistsException)
from pymivot.tap.utils.constant import CONSTANT


class TestManageMivotSchema(unittest.TestCase):
    def setUp(self):
        self.postgresql = Postgresql()
        self.db_params = self.postgresql.dsn()
        self.mivot = ManageMivotSchema()
        self.mivot.login(
            dbms="postgresql",
            port=self.db_params['port'],
            host=self.db_params['host'],
            database=self.db_params['database'],
            user=self.db_params['user'],
            password=None
        )
        self.assertIsNotNone(self.mivot.db.connection)
        self.mivot.db.create_schema(CONSTANT.TAP_SCHEMA)
        self.mivot.tap_schema = CONSTANT.TAP_SCHEMA
        self.mivot.mivot_create_table("mango")
        self.assertTrue(self.mivot.db._table_exists("mango", schema_name=self.mivot.tap_schema))
        self.mivot.db.create_table("tables", columns="table_name TEXT NOT NULL", schema_name=self.mivot.tap_schema, is_model=False)
        self.mivot.db._insert_data("tables", ["table_name"], ["epic_src"], schema_name=self.mivot.tap_schema, is_model=False)

    def test_mivot_add_mapped_class(self):
        self.assertEqual(self.mivot.db.fetch_data("mango", schema_name=CONSTANT.TAP_SCHEMA, columns=["instance_id"]).data, [])
        instance_id = self.mivot.mivot_add_mapped_class("mango", "epic_src", "photometricmeasure", {
            "sc_ra": {"dmrole": "value", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": False}}, "pos.main", "#POS")
        self.assertNotEqual(
            self.mivot.db.fetch_data("mango", schema_name=CONSTANT.TAP_SCHEMA, columns=["instance_id"],
                                     condition=f"instance_id='{instance_id}'").data, [])

        with self.assertRaises(TableAlreadyExistsException):
            self.mivot.mivot_add_mapped_class(
            "mango", "epic_src", "photometricmeasure",
            {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                "pos.main", "#POS", instance_id=instance_id)
            self.mivot.mivot_add_mapped_class(
                "mango", "epic_src", "photometricmeasure",
                {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                "pos.main", "#POS")

        with self.assertRaises(IdAlreadyExistsException):
            self.mivot.mivot_add_mapped_class("mango", "epic_src", "correlatederror1d2d",
                                              {"correlation1_2": {"dmrole": "correlation1_2",
                                                                  "frame": "FK5(eq=J2000, ep=2015)"}},
                                              "pos.main", "#POS")
            self.mivot.mivot_add_mapped_class("mango", "epic_src", "correlatederror1d2d",
                                              {"correlation2_1": {"dmrole": "correlation1_2",
                                                         "frame": "FK5(eq=J2000, ep=2015)"}},
                                              "pos.main", "#POS")

        self.mivot.mivot_drop_mapped_class("mango", instance_id=instance_id)
        self.assertEqual(self.mivot.db.fetch_data("mango", schema_name=CONSTANT.TAP_SCHEMA, columns=["instance_id"],
                                     condition=f"instance_id='{instance_id}'").data, [])
        with self.assertRaises(TableDoesNotExistException):
            self.mivot.mivot_drop_mapped_class("mango", instance_id="fake_instance_id")

        # Test with ucd and vocab parameters set to None (default)
        self.mivot.mivot_add_mapped_class("mango", "epic_src", "multiparamerror",
                                          {"sc_ra": {"dmrole": "unit", "frame": "FK5(eq=J2000, ep=2015)"}})

    def test_mivot_add_error_to_mapped_class(self):
        instance_id = self.mivot.mivot_add_mapped_class("mango", "epic_src", "photometricmeasure", {
            "sc_ra": {"dmrole": "value", "frame": "FK5(eq=J2000, ep=2015)"}}, "pos.main", "#POS")

        self.mivot.mivot_add_error_to_mapped_class("mango", instance_id, "error")
        self.assertNotEqual(
            self.mivot.db.fetch_data("mango", schema_name=CONSTANT.TAP_SCHEMA, columns=["dmerror"],
                                     condition=f"instance_id='{instance_id}'").data, [])

        self.mivot.mivot_drop_error_from_mapped_class("mango", instance_id)
        self.assertEqual(
            self.mivot.db.fetch_data("mango", schema_name=CONSTANT.TAP_SCHEMA, columns=["dmerror"],
                                     condition=f"instance_id='{instance_id}'").data, [(None,)])

        with self.assertRaises(DmtypeInvalidException):
            self.mivot.mivot_add_mapped_class("mango", "epic_src", "meas:LonLatPos",
                                              {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                                              "pos.main", "#POS")

        with self.assertRaises(DmroleInvalidException):
            self.mivot.mivot_add_mapped_class("mango", "epic_src", "ellipse",
                                              {"sc_ra": {"dmrole": "lon", "frame": "FK5(eq=J2000, ep=2015)"}},
                                              "pos.main", "#POS")

    def test_mapping(self):
        self.mivot.db._drop_table("mango", schema_name=self.mivot.tap_schema)
        self.mivot.mivot_create_table("mango")
        epic_src_columns = """photometric_value FLOAT, photometric_photcal FLOAT,
        ellipse_semi_major_axis FLOAT, ellipse_semi_minor_axis FLOAT, diagmatrix FLOAT"""
        self.mivot.db.create_table("epic_src", columns=epic_src_columns, schema_name='public', is_model=False)

        self.mivot.mivot_add_mapped_class("mango", "epic_src", "photometricmeasure", {
            "photometric_value": {"dmrole": "value", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": False},
            "photometric_photcal": {"dmrole": "photcal", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": True},
        }, "pos.main", "#POS")
        self.mivot.mivot_add_mapped_class("mango", "epic_src", "Ellipse", {
            "ellipse_semi_major_axis": {"dmrole": "semimajoraxis", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": True},
            "ellipse_semi_minor_axis": {"dmrole": "semiminoraxis", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": True},
        }, "pos.main", "#POS")
        self.mivot.mivot_add_mapped_class("mango", "epic_src", "diagmatrix2x2", {
            "diagmatrix": {"dmrole": "diagmatrix", "frame": "FK5(eq=J2000, ep=2015)", "mandatory": False}
        }, "pos.main", "#POS")
        self.assertEqual(self.mivot.get_mappeable_classes("mango", "epic_src", ("photometric_value", "photometric_photcal", "ellipse_semi_major_axis", "diagmatrix")), ['__photometricmeasure_main_', '__diagmatrix2x2_main_'])

    def tearDown(self):
        self.mivot.db._drop_table("mango")
        self.mivot.logout()
        self.mivot.db._close_connection()
        self.postgresql.stop()
