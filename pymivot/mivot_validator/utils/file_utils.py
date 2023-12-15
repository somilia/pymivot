"""
Created on Feb 26, 2021

@author: laurentmichel
"""
import os


class FileUtils:
    """
    classdocs
    """

    file_path = os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_datadir():
        """
        get the path to the data directory
        """
        return os.path.realpath(
            os.path.join(FileUtils.file_path, "...instance_checking.tests/", "data")
        )

    @staticmethod
    def get_projectdir():
        """
        get the path to the project directory
        """
        return os.path.realpath(os.path.join(FileUtils.file_path, "../../"))

    @staticmethod
    def get_schemadir():
        """
        get the path to the schema directory
        """
        return os.path.realpath(os.path.join(FileUtils.file_path, "../../", "schema"))
