"""
Created on 2023/03

Test suite validating the whole votables against both schema (VOTable MIVOT)
and the model compliance

@author: laurentmichel
"""
import os, sys
import unittest
from mivot_validator.annotated_votable_validator import AnnotatedVOTableValidator
from astropy.io.votable import parse
from mivot_validator.instance_checking.xml_interpreter.model_viewer import ModelViewer
from mivot_validator.instance_checking.instance_checker import InstanceChecker

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):
    def test6paramOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        table_prefixes = ["gaia_6params", "gaia_3mags"]
        annotated_votable_validator = AnnotatedVOTableValidator()
        files = os.listdir(mapping_sample)
        for table_prefix in table_prefixes:
            for sample_file in files:
                if sample_file.startswith(table_prefix) and "_ok_" in sample_file:
                    file_path = os.path.join(mapping_sample, sample_file)
                    self.assertTrue(annotated_votable_validator.validate(file_path))
                    votable = parse(file_path)

                    mviewer = None
                    for resource in votable.resources:
                        if len(votable.resources) != 1:
                            print(
                                "VOTable with more than one resource are not supported yet"
                            )
                            sys.exit(1)

                        mviewer = ModelViewer(resource, votable_path=file_path)
                        mviewer.connect_table(None)
                        # Seek the first data row
                        mviewer.get_next_row()
                        # and get its model view
                        # The references are resolved in order to be able to check their counterparts
                        model_view = mviewer.get_model_view(resolve_ref=True)
                        # empty the snipper cache
                        InstanceChecker._clean_tmpdata_dir()

                        # Validate all instances  on which the table data are mapped
                        for instance in model_view.xpath(".//INSTANCE"):
                            print(f'CHECKING: instance {instance.get("dmtype")}')
                            InstanceChecker.check_instance_validity(instance)

    def testNotExistingFile(self):
        """
        Check that a non existing file is considered as non valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        self.assertFalse(annotated_votable_validator.validate("/tagada/tsoin/tsoin"))

    def testNotXMLFile(self):
        """
        Check that a non XML file is considered as non valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        self.assertFalse(
            annotated_votable_validator.validate(os.path.realpath(__file__))
        )


if __name__ == "__main__":
    unittest.main()
