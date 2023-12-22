"""
Created on 2022/09

Test suite validating that all role and types of the annotation are consistent with the model they refer to.

@author: laurentmichel
"""
import os
import unittest
from pymivot.validator.mivot_validator.dmtypes_and_role_checker import DmTypesAndRolesChecker

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):
    def testOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        types_and_role_checker = DmTypesAndRolesChecker()
        file_path = os.path.join(mapping_sample, "test_dmtypes_and_roles_ok.xml")
        self.assertTrue(types_and_role_checker.validate(file_path))

    def testKO(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        types_and_role_checker = DmTypesAndRolesChecker()
        file_path = os.path.join(mapping_sample, "test_dmtypes_and_roles_ko.xml")
        self.assertFalse(types_and_role_checker.validate(file_path))
        self.assertListEqual(
            types_and_role_checker.messages, ["unknown dmrole meas:Measure.coord"]
        )


if __name__ == "__main__":
    unittest.main()
