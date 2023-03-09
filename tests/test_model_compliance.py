'''
Created on 22 Feb 2023

Test suite validating that the object instances resulting from the annotation parsing 
are compliant with their VODML class definitions.

XML instances to be checked are provided as XML snippets

@author: laurentmichel
'''
import os
import unittest
import traceback
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.utils.dict_utils import DictUtils

from mivot_validator.instance_checking.instance_checker import (
    InstanceChecker,
    CheckFailedException,
    )
from mivot_validator.instance_checking.xml_interpreter.exceptions import MappingException

mapping_sample = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data")
vodml_sample = os.path.join(os.path.dirname(
    os.path.realpath(__file__)),
    "../mivot_validator/",
    "instance_checking/",
    "vodml/")

class TestModelCompliance(unittest.TestCase):

    def testOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """

        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("instcheck") and "_ok_" in sample_file:
                try:
                    InstanceChecker._clean_tmpdata_dir()
                    instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, sample_file))
                    InstanceChecker.check_instance_validity(instance.getroot())
                    self.assertTrue(True)
                except :
                    traceback.print_exc()
                    self.assertTrue(False, f"{sample_file} not valid")
 
    def testKO(self):
        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_ko_1.xml"))
        try:
            InstanceChecker.check_instance_validity(instance.getroot())
            self.assertTrue(False, "test should fail")
        except CheckFailedException as exp:
            self.assertEqual(str(exp),
                             "No collection with dmrole meas:Asymmetrical2D.plusplus in object type meas:Asymmetrical2D")

        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_ko_2.xml"))
        try:
            InstanceChecker.check_instance_validity(instance.getroot())
            self.assertTrue(False, "test should fail")
        except MappingException as exp:
            print(exp)
            self.assertEqual(str(exp),
                             "Complex type Asymmetrical2DXXX not found")

        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_ko_3.xml"))
        try:
            InstanceChecker.check_instance_validity(instance.getroot())
            self.assertTrue(False, "test should fail")
        except CheckFailedException as exp:
            print(exp)
            self.assertEqual(str(exp),
                             "Duplicated dmrole coords:LonLatPoint.lon")


if __name__ == "__main__":
    unittest.main()