'''
Created on 22 Feb 2023

Test suite validating that the object instances resulting from the annotation parsing 
are compliant with their VODML class definitions

@author: laurentmichel
'''
import os
import unittest
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

class TestInstCheck(unittest.TestCase):

    def testInheritenceGraph(self):
        self.maxDiff = None
        vodml_filepath = os.path.join(vodml_sample, "Meas-v1.vo-dml.xml")
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        self.assertDictEqual(InstanceChecker.inheritence_tree,
                             DictUtils.read_dict_from_file(
                                 os.path.join(mapping_sample, "instcheck_inherit_meas.json"))
                             )
        InstanceChecker.inheritence_tree = {}
        vodml_filepath = os.path.join(vodml_sample, "Coords-v1.0.vo-dml.xml")
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        DictUtils.print_pretty_json(InstanceChecker.inheritence_tree)
        self.assertDictEqual(InstanceChecker.inheritence_tree,
                             DictUtils.read_dict_from_file(
                                 os.path.join(mapping_sample, "instcheck_inherit_coords.json"))
                             )

    def testOK(self):
        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("instcheck_") and "_ok_" in sample_file:
                file_path = os.path.join(mapping_sample, sample_file)
                instance = XmlUtils.xmltree_from_file(file_path)
                status = InstanceChecker.check_instance_validity(instance.getroot())
                self.assertTrue(status)

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

        instance = XmlUtils.xmltree_from_file(os.path.join(mapping_sample, "instcheck_photdm_ko.xml"))
        try:
            InstanceChecker.check_instance_validity(instance.getroot())
            self.assertTrue(False, "test should fail")
        except CheckFailedException as exp:
            print(exp)
            self.assertEqual(str(exp),
                             "Object type Phot:Flux has no component with dmrole=Phot:Flux.ucd and dmtype=UCD type should be Phot:UCD")

    def testModelLocation(self):
        InstanceChecker._clean_tmpdata_dir()
        self.assertTrue(
            InstanceChecker._get_model_location("Meas").endswith("tmp_snippets/Meas-v1.vo-dml.xml")
            )
        self.assertTrue(
            InstanceChecker._get_model_location("coords").endswith("tmp_snippets/Coords-v1.0.vo-dml.xml")
            )
        self.assertTrue(
            InstanceChecker._get_model_location("phot").endswith("tmp_snippets/Phot-v1.vodml.xml")
            )
        self.assertTrue(
            InstanceChecker._get_model_location("ivoa").endswith("tmp_snippets/IVOA-v1.vo-dml.xml")
            )

if __name__ == "__main__":
    unittest.main()