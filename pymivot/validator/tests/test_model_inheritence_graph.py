"""
Created on 2023/03

Test checking that the validator builds correct inheritence trees.


@author: laurentmichel
"""
import os
import unittest
from pymivot.validator.mivot_validator.utils.dict_utils import DictUtils

from pymivot.validator.mivot_validator.instance_checking.instance_checker import (
    InstanceChecker,
)
from pymivot.validator.mivot_validator.instance_checking.inheritance_checker import (
    InheritanceChecker,
)

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
vodml_sample = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "../mivot_validator/",
    "instance_checking/",
    "vodml/",
)


class TestInheritenceGraph(unittest.TestCase):
    def testModelLocation(self):
        InstanceChecker._clean_tmpdata_dir()
        return
        self.assertTrue(
            InstanceChecker._get_model_location("meas").endswith(
                "tmp_snippets/Meas-v1.vo-dml.xml"
            )
        )
        self.assertTrue(
            InstanceChecker._get_model_location("coords").endswith(
                "tmp_snippets/Coords-v1.0.vo-dml.xml"
            )
        )
        self.assertTrue(
            InstanceChecker._get_model_location("phot").endswith(
                "tmp_snippets/Phot-v1.vodml.xml"
            )
        )
        self.assertTrue(
            InstanceChecker._get_model_location("ivoa").endswith(
                "tmp_snippets/IVOA-v1.vo-dml.xml"
            )
        )
        self.assertTrue(
            InstanceChecker._get_model_location("mango").endswith(
                "tmp_snippets/mango.vo-dml.xml"
            )
        )

    def testInheritenceGraph(self):
        return
        self.maxDiff = None
        vodml_filepath = os.path.join(vodml_sample, "Meas-v1.vo-dml.xml")
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        self.assertDictEqual(
            InstanceChecker.inheritence_tree,
            DictUtils.read_dict_from_file(
                os.path.join(mapping_sample, "instcheck_inherit_meas.json")
            ),
        )
        vodml_filepath = os.path.join(vodml_sample, "Coords-v1.0.vo-dml.xml")
        InstanceChecker.inheritence_tree = {}
        InstanceChecker._build_inheritence_graph(vodml_filepath)
        DictUtils.print_pretty_json(InstanceChecker.inheritence_tree)
        self.assertDictEqual(
            InstanceChecker.inheritence_tree,
            DictUtils.read_dict_from_file(
                os.path.join(mapping_sample, "instcheck_inherit_coords.json")
            ),
        )

    def testGetInheritence(self):
        models = ["Meas-v1.vo-dml.xml", "Coords-v1.0.vo-dml.xml"]
        instchecks = ["instcheck_inherit_meas.json", "instcheck_inherit_coords.json"]

        for model, inst in zip(models, instchecks):
            vodml_filepath = os.path.join(vodml_sample, model)
            InstanceChecker._build_inheritence_graph(vodml_filepath)
            check = InheritanceChecker(InstanceChecker.inheritence_tree)
            graph = DictUtils.read_dict_from_file(os.path.join(mapping_sample, inst))
            for k, v in graph.items():
                for el in v:
                    self.assertIn(k, check.get_inheritance(el))

    def testCheckInheritence(self):
        models = ["Meas-v1.vo-dml.xml", "Coords-v1.0.vo-dml.xml"]
        instchecks = ["instcheck_inherit_meas.json", "instcheck_inherit_coords.json"]

        for model, inst in zip(models, instchecks):
            vodml_filepath = os.path.join(vodml_sample, model)
            InstanceChecker._build_inheritence_graph(vodml_filepath)
            check = InheritanceChecker(InstanceChecker.inheritence_tree)
            graph = DictUtils.read_dict_from_file(os.path.join(mapping_sample, inst))
            for k, v in graph.items():
                for el in v:
                    for el2 in v:
                        self.assertTrue(check.check_inheritance(el, el2))


if __name__ == "__main__":
    unittest.main()
