"""

The annotated votables against both schemas (MIVOT and VOTable 1.3)

Created on 2022/07/01
@author: laurentmichel
"""
import os
import unittest
from mivot_validator.annotated_votable_validator import AnnotatedVOTableValidator

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):
    def testOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("test_instance_ok") is True:
                file_path = os.path.join(mapping_sample, sample_file)
                self.assertTrue(annotated_votable_validator.validate(file_path))

    def testKO(self):
        """
        Check that all sample files tagged as KO are actually not valid
        """
        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("test_instance_ko") is True:
                file_path = os.path.join(mapping_sample, sample_file)
                annotated_votable_validator = AnnotatedVOTableValidator()
                self.assertFalse(annotated_votable_validator.validate(file_path))

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
