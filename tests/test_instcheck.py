'''
Created on 22 Feb 2023

@author: laurentmichel
'''
import os
import json
import unittest
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.utils.dict_utils import DictUtils

from mivot_validator.instance_checking.instance_checker import (
    InstanceChecker,
    CheckFailedException,
    )
from mivot_validator.instance_checking.xml_interpreter.exceptions import MappingException

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
vodml_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                  "../mivot_validator/",
                                                  "instance_checking/",
                                                  "vodml/")
class TestInstCheck(unittest.TestCase):

    def testInheritenceGraph(self):
        self.maxDiff = None
        vodml_filepath = os.path.join(vodml_sample, "Meas-v1.vo-dml.xml")
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        self.assertDictEqual(InstanceChecker.inheritence_tree,
                             DictUtils.read_dict_from_file(
                                 os.path.join(mapping_sample, "instcheck_inherit_meas.json"))
                             )
        vodml_filepath = os.path.join(vodml_sample, "Coords-v1.0.vo-dml.xml")
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        self.assertDictEqual(InstanceChecker.inheritence_tree,
                             DictUtils.read_dict_from_file(
                                 os.path.join(mapping_sample, "instcheck_inherit_coords.json"))
                             )


    def testOK(self):
        return
        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_ok_1.xml"))
        status = InstanceChecker.check_instance_validity(instance.getroot())
        self.assertTrue(status)
        
        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_ok_2.xml"))
        status = InstanceChecker.check_instance_validity(instance.getroot())
        self.assertTrue(status)

    def testKO(self):
        return
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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()