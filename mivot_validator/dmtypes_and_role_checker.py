""" 
Created on 2 Feb 2023

@author: laurentmichel
"""
import os
import ssl
from urllib.request import urlopen
from lxml import etree
from . import logger

# This restores the same behavior as before.
context = ssl._create_unverified_context()


class DmTypesAndRolesChecker(object):
    """
    This module checks that all dmroles and dmtypes used a referenced in the mapped models
    This is a prototype
    - Only meas/coord/ivoa are checked, the other models are ignored
    - The checking is based on the vodml-id whatever their context in the vodml files

    all errors are reported in the self.message list. 
    The validation is considered as successful if the message list is empty at the end of the process
    """

    def __init__(self):
        self.model_roles = {}
        self.model_types = {}
        self.models = []
        self.messages = []
        self.__get_model_types(
            "coords", "https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml"
        )
        self.__get_model_types("meas", "https://ivoa.net/xml/VODML/Meas-v1.vo-dml.xml")
        self.__get_model_types(
            "ivoa", "https://ivoa.net/xml/VODML/20180519/IVOA-v1.0.vo-dml.xml"
        )

    def __get_model_types(self, name, url):
        """
        store roles and types of the model components
        :param name: model name
        :type name: string
        :param url: URL of the vodml
        :type url: string
        """
        if name not in self.model_roles.keys():
            self.model_roles[name] = []
        if name not in self.model_types.keys():
            self.model_types[name] = []

        with urlopen(url, context=context) as f:
            vodml = etree.parse(f)
            for ele in vodml.xpath(".//objectType/vodml-id"):
                self.model_types[name].append(f"{name}:{ele.text}")
            for ele in vodml.xpath(".//dataType/vodml-id"):
                self.model_types[name].append(f"{name}:{ele.text}")
            for ele in vodml.xpath(".//primitiveType/vodml-id"):
                self.model_types[name].append(f"{name}:{ele.text}")
            for ele in vodml.xpath(".//attribute/vodml-id"):
                self.model_roles[name].append(f"{name}:{ele.text}")
            for ele in vodml.xpath(".//composition/vodml-id"):
                self.model_roles[name].append(f"{name}:{ele.text}")

    def validate(self, file_path):
        """
        Validate that all dmroles and types found in the mapping block are
        part of the declared models.
        the method returns false if at least one error message has been collected
        :param file_path: file  path to be evaluated
        :type file_path: string
        :return: true if the file is valid
        :rtype: boolean
        """

        self.messages = []

        if os.path.exists(file_path) is False:
            self.messages.append(f"Path {file_path} does not exist")
            return False

        if os.path.isdir(file_path) is True:
            self.messages.append(f"Path {file_path} is a directory")
            return False

        if self.__is_xml(file_path) is False:
            self.messages.append(f"File {file_path} does not look like XML")
            return False

        # Get the filename for the log messages
        file_name = os.path.basename(file_path)
        logger.info(f"Check types and roles from file {file_name}")
        root = etree.parse(file_path).getroot()
        for ele in root.xpath("//*"):
            tag = ele.tag
            if tag.endswith("MODEL"):
                self.models.append(ele.get("name"))
            elif tag.endswith("INSTANCE"):
                self._check_instance(ele)
            elif tag.endswith("ATTRIBUTE"):
                self._check_instance(ele)
            elif tag.endswith("COLLECTION"):
                self._check_instance(ele)

        return len(self.messages) == 0

    def _check_instance(self, ele):
        """
        checks the XML element has both dmtype and dmrole (if exists) recorded in the mapped models.
        errors are recorded in self.messages
        :param ele: XML element to check (INSTANCE/COLLECTION/ATTRIBUTE)
        :type ele: etree element
        """

        # check the types
        dmtype = ele.get("dmtype")
        if not dmtype:
            return
        items = dmtype.split(":")
        if len(items) != 2:
            message = f"dmtype {dmtype} badly formed"
            if message not in self.messages:
                self.messages.append(message)
        if (
            items[0] in self.model_types.keys()
            and dmtype not in self.model_types[items[0]]
        ):
            message = f"unknown dmtype {dmtype}"
            if message not in self.messages:
                self.messages.append(message)

        # check the roles
        dmrole = ele.get("dmrole")
        if not dmrole:
            return
        items = dmrole.split(":")
        if len(items) != 2:
            message = f"dmrole {dmrole} badly formed"
            if message not in self.messages:
                self.messages.append(message)
        if (
            items[0] in self.model_roles.keys()
            and dmrole not in self.model_roles[items[0]]
        ):
            message = f"unknown dmrole {dmrole}"
            if message not in self.messages:
                self.messages.append(message)

    def __is_xml(self, file_path):
        """
        :param file_path: file path ot be evaluated
        :type file_path: string
        :return: true if file_path is an XML file (test based on the prolog)
        :rtype: boolean
        """
        try:
            with open(file_path) as unknown_file:
                prolog = unknown_file.read(45)
                return prolog.startswith("<?xml") is True
        except Exception:
            pass
        return False
