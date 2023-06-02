"""
Created on 21 Apr 2023

use the snippet_builder to build a concrete MIVOT view of
the class model_name:class_name of the model
serialized in provided generic MIVOT snippet

@author: julien abid
"""

import os
import ssl
from urllib.parse import urlparse
from urllib.request import urlretrieve

from lxml import etree

from mivot_validator.instance_checking.snippet_builder import Builder
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.instance_checking.instance_checker import InstanceChecker


class BColors:
    """
    Color codes for terminal output
    """

    GRAY = "\033[37m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    RED = "\033[31m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class InstanceBuilder:
    """
    Build a concrete MIVOT view of the class model_name:class_name of the model
    serialized in provided generic MIVOT snippet
    """

    def __init__(self, xml_file, output_dir, output_name, concrete_list=None):
        """
        :xml_file: path to the generic MIVOT
        :output_dir: path to the output directory
        :model_xml: path to the model xml file
        :abstract_classes: list of abstract classes
        :buffer: temporary content of the output file
        :build_file: actual path of the file being built (recursively)
        :dmrole: dmrole of the current instance
        :dmroles: list of dmroles in the snippet
        """
        self.xml_file = xml_file
        self.output_dir = output_dir
        self.output_name = output_name
        self.buffer = ""
        self.build_file = self.xml_file
        self.dmrole = None
        self.dmroles = []
        self.dmtype = None
        self.concrete_list = concrete_list
        self.inheritance_graph = {
            **InstanceChecker._build_inheritence_graph(
                "../vodml/mango.vo-dml.xml"
            ),
            **InstanceChecker._build_inheritence_graph(
                "../vodml/Phot-v1.1.vodml.xml"
            ),
            **InstanceChecker._build_inheritence_graph(
                "../vodml/Coords-v1.0.vo-dml.xml"
            ),
            **InstanceChecker._build_inheritence_graph(
                "../vodml/Meas-v1.vo-dml.xml"
            ),
        }
        self.abstract_classes = list(self.inheritance_graph.keys())

    def build(self):
        """
        Build the concrete MIVOT snippet
        """
        if not os.path.exists("../tmp_snippets/temp"):
            os.makedirs("../tmp_snippets/temp")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        parent_key = None
        open_count = 0
        property_count = 0
        with open(self.build_file, "r", encoding="utf-8") as file:
            for line in file:
                if "left blank" not in line:
                    self.buffer += line
                if "</INSTANCE" in line:
                    open_count -= 1
                    if open_count == 0:
                        parent_key = None
                if "<INSTANCE" in line:
                    if "/>" not in line:
                        open_count += 1
                    if parent_key is None:
                        parent_key = self.get_dm_type(line)
                    if self.get_dm_type(line) in self.abstract_classes:
                        self.dmrole = self.get_dm_role(line)
                        print("@@@@@@", self.dmrole)
                        self.dmtype = self.get_dm_type(line)
                        if self.dmrole == "mango:Property.associatedProperties":
                            self.dmroles.append("")
                        else:
                            self.dmroles.append(self.dmrole)
                        print(
                            f"{BColors.OKCYAN}{BColors.UNDERLINE}"
                            f"List of possible concrete classes :{BColors.ENDC}"
                        )
                        print(
                            f"{BColors.OKCYAN}DMTYPE: {BColors.BOLD}"
                            f"{self.get_dm_type(line)}{BColors.ENDC}"
                        )
                        print(
                            f"{BColors.OKCYAN}CONTEXT: {BColors.BOLD}"
                            f"{parent_key}{BColors.ENDC}"
                        )
                        print(
                            f"{BColors.OKCYAN}DMROLE: {BColors.BOLD}"
                            f"{self.dmrole}{BColors.ENDC}"
                        )
                        if property_count == 0:
                            choice = self.populate_choices(
                                self.inheritance_graph[self.get_dm_type(line)],
                                parent_key,
                            )
                            file = None
                            if choice != "None":
                                file = self.get_instance(
                                    choice.split(":")[0], choice.split(":")[1]
                                )
                            if file is not None:
                                if self.get_dm_type(line) == "mango:Property":
                                    property_count += 1
                                self.buffer = self.buffer.replace(line, "")
                                self.build_file = file
                                self.build()
                                self.build_file = self.xml_file
                        if property_count > 0:
                            property_dock = True
                            while property_dock:
                                property_dock = self.ask_for_property(parent_key)
                                if property_dock:
                                    property_count += 1
                                    choice = self.populate_choices(
                                        self.inheritance_graph[self.get_dm_type(line)],
                                        parent_key,
                                    )
                                    if choice != "None":
                                        file = self.get_instance(
                                            choice.split(":")[0], choice.split(":")[1]
                                        )
                                        if file is not None:
                                            self.build_file = file
                                            self.build()
                                            self.build_file = self.xml_file
                                    else:
                                        self.dmroles[
                                            self.dmroles.index(
                                                "mango:Property:associatedProperty"
                                            )
                                        ].pop()
                            property_count -= 1

    def output_result(self):
        """
        Write the concrete MIVOT snippet in the output directory
        """

        if not self.output_name.endswith(".xml"):
            self.output_name += ".xml"
        output_file = os.path.join(self.output_dir, os.path.basename(self.output_name))
        result = etree.fromstring(self.buffer)
        XmlUtils.xmltree_to_file(result, output_file)

        self.clean(output_file)
        self.insert_dm_roles(output_file, self.dmroles)

        if os.path.exists("../tmp_snippets/temp"):
            os.system("rm -rf ../tmp_snippets/temp")

        print(
            f"{BColors.OKGREEN}Concrete MIVOT snippet for "
            f"{BColors.BOLD}{os.path.basename(self.xml_file)} stored in "
            f"{BColors.BOLD}{output_file}{BColors.ENDC}"
        )

    def ask_for_property(self, parent_key):
        """
        Ask the user if he wants to add another property in the collection

        :param parent_key: the context of the property
        """
        state = None
        print(
            f"{BColors.OKCYAN} Do you want to add another Property in this collection"
            f" for {parent_key}? (y/n){BColors.ENDC}"
        )
        choice = input()
        if choice == "y":
            state = True
        elif choice == "n":
            state = False
        else:
            print(f"{BColors.WARNING}Please enter a valid choice{BColors.ENDC}")
            self.ask_for_property(parent_key)

        return state

    @staticmethod
    def remove_instance(xml_file, dmtype):
        """
        Remove the instance of a class containing given dmtype and all its children
        """
        with open(xml_file, "r", encoding="utf-8") as file:
            buffer = ""
            counter = 0
            is_dmtype = False
            for line in file:
                if counter == 0:
                    buffer += line
                if f'dmtype="{dmtype}"' in line:
                    is_dmtype = True
                if "<INSTANCE" in line and "/>" not in line and is_dmtype:
                    counter += 1
                if "</INSTANCE" in line:
                    counter -= 1

        with open(xml_file, "w", encoding="utf-8") as file:
            file.write(buffer)

    @staticmethod
    def clean(xml_file):
        """
        Remove all collections with no concrete instances
        """
        buffer = ""
        counter = []
        to_remove = False
        temp = []

        with open(xml_file, "r", encoding="utf-8") as file:
            i = 0
            for line in file:
                if "<COLLECTION" in line:
                    temp.append(i)
                elif 'dmtype="mango:Property"' in line:
                    to_remove = True
                    temp.append(i)
                elif "</COLLECTION" in line:
                    if to_remove:
                        to_remove = False
                        temp.append(i)
                        counter.extend(temp)
                    else:
                        temp.clear()
                else:
                    temp.clear()
                i += 1

        with open(xml_file, "r", encoding="utf-8") as file:
            i = 0
            for line in file:
                if i not in counter:
                    buffer += line
                i += 1

        with open(xml_file, "w", encoding="utf-8") as file:
            file.write(buffer)

    def insert_dm_roles(self, xml_file, dmroles):
        """
        Insert the dmroles in the concrete MIVOT snippet
        """
        print(dmroles)
        with open(xml_file, "r", encoding="utf-8") as file:
            buffer = ""
            for line in file:
                if 'dmrole=""' in line:
                    print("@@@@@@", line)
                    dmrole = dmroles.pop(0) if len(dmroles) > 0 else ""
                    line = line.replace('dmrole=""', f'dmrole="{dmrole}"')
                buffer += line

        with open(xml_file, "w", encoding="utf-8") as file:
            file.write(buffer)

    @staticmethod
    def get_model_xml_from_name(model_name):
        """
        Get the model XML from the MIVOT snippet
        :return: the model XML
        """
        local_vodml_path = None

        ssl.create_default_context().check_hostname = False

        if model_name == "meas":
            if urlparse("https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir,
                    os.path.basename("https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml"),
                )
                urlretrieve(
                    "https://ivoa.net/xml/VODML/Meas-v1.0.vo-dml.xml", local_vodml_path
                )

        elif model_name == "coords":
            if urlparse("https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir,
                    os.path.basename(
                        "https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml"
                    ),
                )
                urlretrieve(
                    "https://ivoa.net/xml/VODML/Coords-v1.0.vo-dml.xml",
                    local_vodml_path,
                )
        elif model_name == "ivoa":
            if urlparse("https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir,
                    os.path.basename("https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml"),
                )
                urlretrieve(
                    "https://ivoa.net/xml/VODML/IVOA-v1.vo-dml.xml", local_vodml_path
                )
        elif model_name == "Phot":
            if urlparse("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml").scheme:
                temp_dir = "tmp_vodml"
                os.makedirs(temp_dir, exist_ok=True)
                local_vodml_path = os.path.join(
                    temp_dir,
                    os.path.basename("https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml"),
                )
                urlretrieve(
                    "https://ivoa.net/xml/VODML/Phot-v1.1.vodml.xml", local_vodml_path
                )
        elif model_name == "instfov":
            local_vodml_path = "../vodml/instfov.vo-dml.xml"
        elif model_name == "mango":
            local_vodml_path = "../vodml/mango.vo-dml.xml"

        if local_vodml_path is not None:
            return os.path.abspath(local_vodml_path)

        return None

    def get_instance(self, model_name, class_name):
        """
        Get the instance of the class class_name of the model model_name
        :return: the instance path
        """
        builder = Builder(
            model_name,
            class_name,
            self.get_model_xml_from_name(model_name),
            "../tmp_snippets/temp",
        )
        builder.build()

        return builder.outputname

    @staticmethod
    def get_dm_role(line):
        """
        Get the dmrole from the line
        :return: the dmrole
        """
        dmrole = ""
        if "dmrole" in line:
            dmrole = line.split("dmrole")[1].split('"')[1]

        return dmrole

    @staticmethod
    def get_dm_type(line):
        """
        Get the dmtype from the line
        :return: the dmtype
        """
        dmtype = ""
        if "dmtype" in line:
            dmtype = line.split("dmtype")[1].split('"')[1]

        return dmtype

    def populate_choices(self, elements, parent_key):
        """
        Make an input with choices from the list
        """
        clean_elements = []
        for element in elements:
            if element not in clean_elements:
                clean_elements.append(element)

        if self.concrete_list is not None and len(self.concrete_list) > 0:
            for cc_dict in self.concrete_list:
                if (
                        self.dmrole == cc_dict["dmrole"]
                        and self.dmtype == cc_dict["dmtype"]
                        and self.dmtype == cc_dict["dmtype"]
                ):
                    self.concrete_list.pop(self.concrete_list.index(cc_dict))
                    return cc_dict["class"]
        else:
            if parent_key in [
                "mango:Status",
                "mango:Label",
                "mango:Shape",
                "mango:ComputedProperty",
                "mango:PhysicalProperty",
                "mango:BitField",
                "mango:Color",
            ]:
                clean_elements.append("None")

            print(f"{BColors.OKBLUE}Please choose from the list below : {BColors.ENDC}")

            for i, clean_element in enumerate(clean_elements):
                print(f"{BColors.GRAY}{str(i)} : {clean_element}{BColors.ENDC}")

            choice = input("Your choice : ")

            if choice.isdigit() and int(choice) < len(clean_elements):
                return clean_elements[int(choice)]
        print(f"{BColors.WARNING}Wrong choice, please try again.{BColors.ENDC}")
        return self.populate_choices(elements, parent_key)
