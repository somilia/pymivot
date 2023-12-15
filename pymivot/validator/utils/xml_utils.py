"""
Created on 16 Dec 2021

@author: laurentmichel
"""
from unittest import TestCase
import xmltodict
from lxml import etree


class XmlUtils:
    """
    classdocs
    """

    @staticmethod
    def pretty_print(xmltree):
        """
        pretty print an xml tree
        """
        print(XmlUtils.pretty_string(xmltree))

    @staticmethod
    def pretty_string(xmltree):
        """
        pretty print a xml tree and return it as a string
        """
        etree.indent(xmltree, space="   ")
        return etree.tostring(xmltree, pretty_print=True).decode("utf-8")

    @staticmethod
    def xmltree_from_file(file_path):
        """
        return an xml tree from a file
        """
        return etree.parse(file_path)

    @staticmethod
    def xmltree_to_file(xmltree, file_path):
        """
        write a xml tree to a file
        """
        with open(file_path, "w", encoding="utf-8") as output:
            output.write(XmlUtils.pretty_string(xmltree))

    @staticmethod
    def assertXmltreeEquals(xmltree1, xmltree2, message):
        """
        Compare two xml trees
        """
        dict1 = xmltodict.parse(etree.tostring(xmltree1))
        dict2 = xmltodict.parse(etree.tostring(xmltree2))
        TestCase().assertDictEqual(dict1, dict2, message)

    @staticmethod
    def assertXmltreeEqualsFile(xmltree1, xmltree2_file, message=""):
        """
        Compare a xml tree with a file
        """
        testcase = TestCase()
        testcase.maxDiff = None
        dict1 = xmltodict.parse(etree.tostring(xmltree1))
        dict2 = xmltodict.parse(
            etree.tostring(XmlUtils.xmltree_from_file(xmltree2_file))
        )
        testcase.assertDictEqual(dict1, dict2, message)

    @staticmethod
    def set_column_indices(mapping_block, index_map):
        """
        add column ranks to attribute having a ref.
        Using ranks allow to identify columns even numpy raw have been serialised as []
        """
        for ele in mapping_block.xpath("//ATTRIBUTE"):
            ref = ele.get("ref")
            if ref is not None and ref != "NotSet":
                ele.attrib["index"] = str(index_map[ref])

    @staticmethod
    def set_column_units(mapping_block, unit_map):
        """
        add field unit to attribute having a ref.
        Used for performing unit conversions
        """
        for ele in mapping_block.xpath("//ATTRIBUTE"):
            ref = ele.get("ref")
            if ref is not None and ref != "NotSet":
                unit = unit_map[ref]
                if unit is None:
                    unit = ""
                else:
                    unit = str(unit)
                ele.attrib["unit_org"] = unit

    @staticmethod
    def get_attribute_by_role(model_view, dmrole):
        """
        get an attribute by its dmrole
        """
        if model_view is None:
            return None
        for ele in model_view.xpath(f'.//ATTRIBUTE[@dmrole="{dmrole}"]'):
            return ele
        return None

    @staticmethod
    def get_attribute_value_by_role(model_view, dmrole):
        """
        get an attribute value by its dmrole
        """
        if model_view is None:
            return None
        for ele in model_view.xpath(f'.//ATTRIBUTE[@dmrole="{dmrole}"]'):
            return ele.get("value")
        return None

    @staticmethod
    def get_instance_by_role(model_view, dmrole):
        """
        get an instance by its dmrole
        """
        if model_view is None:
            return None
        for ele in model_view.xpath(f'.//INSTANCE[@dmrole="{dmrole}"]'):
            return ele
        return None

    @staticmethod
    def get_instance_by_type(model_view, dmtype):
        """
        get an instance by its dmtype
        """
        if model_view is None:
            return None
        for ele in model_view.xpath(f'.//INSTANCE[@dmrole="{dmtype}"]'):
            return ele
        return None
