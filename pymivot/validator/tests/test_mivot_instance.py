"""
Created on 2022/09

Test suite validating the annotation blocks extracted from annotated 
VOTables against the MIVOT schema 

@author: laurentmichel
"""
import os
import unittest
from pymivot.validator.annotated_votable_validator import AnnotatedVOTableValidator

mapping_sample = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


class Test(unittest.TestCase):
    def testOK(self):
        """
        Check that all sample files tagged as OK are actually valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("test_") and "_ok_" in sample_file:
                file_path = os.path.join(mapping_sample, sample_file)
                self.assertTrue(annotated_votable_validator.validate_mivot(file_path))

    def testKO(self):
        """
        Check that all sample files tagged as KO are actually not valid
        """
        files = os.listdir(mapping_sample)
        for sample_file in files:
            if sample_file.startswith("test_") and "_ko_" in sample_file:
                file_path = os.path.join(mapping_sample, sample_file)
                annotated_votable_validator = AnnotatedVOTableValidator()
                self.assertFalse(annotated_votable_validator.validate_mivot(file_path))

    def testNotExistingFile(self):
        """
        Check that a non existing file is considered as non valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        self.assertFalse(
            annotated_votable_validator.validate_mivot("/tagada/tsoin/tsoin")
        )

    def testNotXMLFile(self):
        """
        Check that a non XML file is considered as non valid
        """
        annotated_votable_validator = AnnotatedVOTableValidator()
        self.assertFalse(
            annotated_votable_validator.validate_mivot(os.path.realpath(__file__))
        )


if __name__ == "__main__":
    unittest.main()
