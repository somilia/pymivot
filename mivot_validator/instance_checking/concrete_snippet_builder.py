"""
Created on 21 Apr 2023

use the snippet_builder to build a concrete MIVOT view of
the class model_name:class_name of the model
serialized in provided generic MIVOT snippet

@author: julien abid
"""

import json
import os
from urllib.parse import urlparse
from urllib.request import urlretrieve

from lxml import etree

from mivot_validator.instance_checking.snippet_builder import Builder
from mivot_validator.utils.xml_utils import XmlUtils


class bcolors:
    """
    Color codes for terminal output
    """
    GRAY = '\033[37m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ConcreteBuilder:
    """
    Build a concrete MIVOT view of the class model_name:class_name of the model
    serialized in provided generic MIVOT snippet
    """

    def __init__(self, xml_file, output_dir, output_name):
        """
        :xml_file: path to the generic MIVOT
        :output_dir: path to the output directory
        :model_xml: path to the model xml file
        :data: json data of the model
        :abstract_classes: list of abstract classes
        :buffer: temporary content of the output file
        :build_file: actual path of the file being built (recursively)
        :dmrole: dmrole of the current instance
        :dmroles: list of dmroles in the snippet
        """
        self.xml_file = xml_file
        self.output_dir = output_dir
        self.model_xml = self.getModelXMLFromName(self.getModelName(self.xml_file))
        self.output_name = output_name
        self.data = json.load(open(os.path.abspath("../vodml/model-logic.json"), "r"))
        self.abstract_classes = self.data["abstract"]
        self.buffer = ""
        self.build_file = self.xml_file
        self.dmrole = None
        self.dmroles = []

    def build(self):
        if not os.path.exists("../tmp_snippets/temp"):
            os.makedirs("../tmp_snippets/temp")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        parent_key = None
        open_count = 0
        property_count = 0
        f = open(self.build_file, "r")
        for line in f:
            if not line.__contains__("left blank"):
                self.buffer += line
            if line.__contains__("</INSTANCE"):
                open_count -= 1
                if open_count == 0:
                    parent_key = None
            if line.__contains__("<INSTANCE"):
                if not line.__contains__("/>"):
                    open_count += 1
                if parent_key is None:
                    parent_key = self.getDmType(line)
                if self.getDmType(line) in self.abstract_classes:
                    self.dmrole = self.getDmRole(line)
                    self.dmroles.append(self.dmrole)
                    print(f"{bcolors.OKCYAN}{bcolors.UNDERLINE}List of possible concrete classes for "
                          f"{bcolors.BOLD}{self.getDmType(line)} in {bcolors.BOLD}{parent_key},"
                          f" with dmrole {self.dmrole}: {bcolors.ENDC}")
                    if property_count == 0:
                        choice = self.populateChoices(
                            list(self.search(self.data, parent_key, self.getDmType(line)))
                        )
                        file = None
                        if choice != "None":
                            file = self.getInstance(choice.split(":")[0], choice.split(":")[1])
                        if file is not None:
                            if self.getDmType(line) == "mango:Property":
                                property_count += 1
                            self.buffer = self.buffer.replace(line, "")
                            self.build_file = file
                            self.build()
                            self.build_file = self.xml_file
                    if property_count > 0:
                        property_dock = True
                        while property_dock:
                            property_dock = self.askForProperty(parent_key)
                            if property_dock:
                                property_count += 1
                                choice = self.populateChoices(
                                    ["mango:Status", "mango:Label", "mango:Shape",
                                     "mango:ComputedProperty", "mango:PhysicalProperty", "None"]
                                )
                                if choice != "None":
                                    file = self.getInstance(choice.split(":")[0], choice.split(":")[1])
                                    if file is not None:
                                        self.build_file = file
                                        self.build()
                                        self.build_file = self.xml_file

        f.close()

    def outputResult(self):
        """
        Write the concrete MIVOT snippet in the output directory
        """
        if not self.output_name.endswith(".xml"):
            self.output_name += ".xml"
        output_file = os.path.join(self.output_dir, os.path.basename(self.output_name))
        result = etree.fromstring(self.buffer)
        XmlUtils.xmltree_to_file(result, output_file)

        self.insertDmRoles(output_file, self.dmroles)

        if os.path.exists("../tmp_snippets/temp"):
            os.system("rm -rf ../tmp_snippets/temp")

        print(f"{bcolors.OKGREEN}Concrete MIVOT snippet for {bcolors.BOLD}{os.path.basename(self.xml_file)} stored in "
              f"{bcolors.BOLD}{output_file}{bcolors.ENDC}")

    def askForProperty(self, parent_key):
        print(f"{bcolors.OKCYAN} Do you want to add another Property in this collection"
              f" for {parent_key}? (y/n){bcolors.ENDC}")
        choice = input()
        if choice == "y":
            return True
        elif choice == "n":
            return False
        else:
            print(f"{bcolors.WARNING}Please enter a valid choice{bcolors.ENDC}")
            self.askForProperty(parent_key)

    @staticmethod
    def removeInstance(xml_file, dmtype):
        """
        Remove the instance of a class containing given dmtype and all its children
        """
        f = open(xml_file, "r")
        buffer = ""
        counter = 0
        is_dmtype = False
        for line in f:
            if counter == 0:
                buffer += line
            if line.__contains__(f'dmtype="{dmtype}"'):
                is_dmtype = True
            if line.__contains__("<INSTANCE") and not line.__contains__("/>") and is_dmtype:
                counter += 1
            if line.__contains__("</INSTANCE"):
                counter -= 1

        f.close()
        f = open(xml_file, "w")
        f.write(buffer)
        f.close()
    def insertDmRoles(self, file, dmroles):
        """
        Insert the dmroles in the concrete MIVOT snippet
        """
        f = open(file, "r")
        buffer = ""

        first = True
        for line in f:
            if line.__contains__('dmrole=""'):
                if first:
                    first = False
                elif not first:
                    dmrole = dmroles.pop(0) if len(dmroles) > 0 else ""
                    line = line.replace('dmrole=""', f'dmrole="{dmrole}"')
            buffer += line

        f.close()
        f = open(file, "w")
        f.write(buffer)
        f.close()

    def getModelName(self, xml_file):
        """
        Get the model name from the MIVOT snippet name
        :return: the model name
        """
        return os.path.basename(xml_file).split('.')[0].split('_')[0].split('-')[0].lower()

    def getClassName(self, xml_file):
        """
        Get the class name from the MIVOT snippet name
        :return: the class name
        """
        return os.path.basename(xml_file).split('.')[1].split('_')[0]

    @staticmethod
    def getModelXMLFromName(model_name):
        """
        Get the model XML from the MIVOT snippet
        :return: the model XML
        """
        local_vodml_path = None
        if model_name == "meas":
            if urlparse("https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir, os.path.basename("https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml"))
                urlretrieve("https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml", local_vodml_path)

        elif model_name == "coords":
            if urlparse("https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir, os.path.basename("https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml"))
                urlretrieve("https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml", local_vodml_path)
        elif model_name == "ivoa":
            if urlparse("https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir, os.path.basename("https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml"))
                urlretrieve("https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml", local_vodml_path)
        elif model_name == "Phot":
            if urlparse("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir, os.path.basename("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml"))
                urlretrieve("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml", local_vodml_path)
        elif model_name == "instfov":
            if urlparse("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir, os.path.basename("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml"))
                urlretrieve("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml", local_vodml_path)


        elif model_name == "mango":
            local_vodml_path = "../vodml/mango.vo-dml.xml"

        return os.path.abspath(local_vodml_path)

    def getInstance(self, model_name, class_name):
        """
        Get the instance of the class class_name of the model model_name
        :return: the instance path
        """
        builder = Builder(model_name, class_name, self.getModelXMLFromName(model_name), "../tmp_snippets/temp")
        builder.build()

        return builder.outputname

    @staticmethod
    def getStringFromFile(file):
        """
        Get the file content as a string
        :return: the file content
        """
        return open(file, "r").read()

    @staticmethod
    def getDmRole(line):
        """
        Get the dmrole from the line
        :return: the dmrole
        """
        if line.__contains__("dmrole"):
            dmrole = line.split("dmrole")[1].split('"')[1]

            return dmrole

    @staticmethod
    def getDmType(line):
        """
        Get the dmtype from the line
        :return: the dmtype
        """
        if line.__contains__("dmtype"):
            dmtype = line.split("dmtype")[1].split('"')[1]

            return dmtype

    def search(self, data, parent_key, key):
        """
        Search for values associated with key who is a child of parent_key
        :return: the values
        """
        if isinstance(data, dict):
            for k, v in data.items():
                if k == parent_key:
                    if key in v:
                        if isinstance(v[key], list):
                            for item in v[key]:
                                yield item
                        else:
                            for key in v[key]:
                                yield key
                else:
                    yield from self.search(v, parent_key, key)
        elif isinstance(data, list):
            for item in data:
                yield from self.search(item, parent_key, key)

    def populateChoices(self, elements):
        """
        Make an input with choices from the list
        """
        clean_elements = []
        for element in elements:
            if element not in clean_elements:
                clean_elements.append(element)

        print(f"{bcolors.OKBLUE}Please choose from the list above : {bcolors.ENDC}")

        for i in range(len(clean_elements)):
            print(f"{bcolors.GRAY}{str(i)} : {clean_elements[i]}{bcolors.ENDC}")

        choice = input("Your choice : ")

        if choice.isdigit() and int(choice) < len(elements):
            return clean_elements[int(choice)]
        else:
            print(f"{bcolors.WARNING}Wrong choice, please try again.{bcolors.ENDC}")
            return self.populateChoices(elements)
