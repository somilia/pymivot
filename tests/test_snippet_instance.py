'''
Testing generations of concrete snippets

Created on 9 May 2023
@author: julien abid
'''
import unittest
import os
import filecmp
from time import sleep

from unittest.mock import patch
from mivot_validator.launchers.instance_snippet_launcher import check_args
from mivot_validator.instance_checking.instance_snippet_builder import InstanceBuilder

OUTPUT = os.getcwd() + "/../tmp_snippets/"
CLASS_NAME = check_args("meas:Position", 0)
FILE_NAME = "meas.Position.res"
REF_FILE_NAME = "meas.Position.test"
CLASSES_LIST = ["meas:Symmetrical", "meas:Asymmetrical2D", "coords:LonLatPoint", "coords:CustomRefLocation",
                "coords:LonLatPoint", "coords:StdRefLocation", "coords:LonLatPoint", "coords:StdRefLocation"]


class Test(unittest.TestCase):

    @classmethod
    def setUp(cls):
        if os.path.exists(OUTPUT + FILE_NAME + ".xml"):
            os.system("rm " + OUTPUT + FILE_NAME + ".xml")
            os.system("rm -rf " + os.getcwd() + "/tmp_vodml")

    @classmethod
    def tearDown(cls):
        filecmp.clear_cache()
        print(os.getcwd() + "/tmp_vodml")
        if os.path.exists(OUTPUT + FILE_NAME + ".xml"):
            os.system("rm " + OUTPUT + FILE_NAME + ".xml")
            os.system("rm -rf " + os.getcwd() + "/tmp_vodml")

    @classmethod
    def tearDownClass(cls):
        for file in os.listdir(OUTPUT):
            if file != ".gitkeep":
                os.remove(OUTPUT + file)

    def testFileExist(self):
        '''
        Check that files are generated in the given directory with the right name
        '''
        # Given
        snippet = InstanceBuilder(CLASS_NAME, OUTPUT, FILE_NAME, CLASSES_LIST)

        # When
        snippet.build()
        snippet.output_result()

        # Then
        self.assertTrue(os.path.exists(OUTPUT + FILE_NAME + ".xml"))

    def testFileCohesion(self):
        '''
        Check that file generated in the given directory have the same content as the test data
        '''
        # Given
        snippet = InstanceBuilder(CLASS_NAME, OUTPUT, FILE_NAME, CLASSES_LIST)

        # When
        snippet.build()
        snippet.output_result()

        # Then
        if os.path.exists(OUTPUT + FILE_NAME + ".xml"):
            self.assertTrue(filecmp.cmp
                            (OUTPUT + FILE_NAME + ".xml",
                             os.path.realpath(os.getcwd() + "/../../../tests/data/" + REF_FILE_NAME + ".xml"),
                             shallow=False))


if __name__ == '__main__':
    unittest.main()
