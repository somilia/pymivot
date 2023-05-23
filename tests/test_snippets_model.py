"""
Testing generations of generic snippets from a VODML-Model file

Created on 9 May 2023
@author: julien abid
"""
import unittest
import os

from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.instance_checking.model_snippets_builder import ModelBuilder

OUTPUT = os.path.abspath(os.getcwd() + "/../tmp_snippets/coords/")
MODEL = os.getcwd() + "/../vodml/Coords-v1.0.vo-dml.xml"
MODEL_NAME = "coords"


def getObjectTypes(model):
    """
    Get the object types of the given model which are not abstract
    """
    res = []

    for ele in model.xpath(f".//objectType"):
        if ele.get("abstract") == "true":
            continue
        for tags in ele.getchildren():
            if tags.tag == "vodml-id":
                res.append(tags.text)
    return res


class Test(unittest.TestCase):
    @classmethod
    def setUp(cls):
        if os.path.exists(OUTPUT):
            os.system("rm -rf " + OUTPUT)

    @classmethod
    def tearDown(cls):
        if os.path.exists(OUTPUT):
            os.system("rm -rf " + OUTPUT)

    def testFilesExists(self):
        """
        Check that files are generated in the given directory
        """
        # Given
        snippets = ModelBuilder(MODEL, None)

        # When
        snippets.build()

        # Then
        self.assertTrue(len(os.listdir(OUTPUT)) > 0)

    def testFilesCohesion(self):
        """
        Check that files generated in the given directory
        are the object types of the model
        """
        # Given
        snippets = ModelBuilder(MODEL, None)
        object_types = getObjectTypes(XmlUtils.xmltree_from_file(MODEL))

        # When
        snippets.build()

        # Then
        for obj in object_types:
            print(OUTPUT + "/" + MODEL_NAME + "." + obj + ".xml")
            self.assertTrue(
                os.path.exists(OUTPUT + "/" + MODEL_NAME + "." + obj + ".xml")
            )


if __name__ == "__main__":
    unittest.main()
