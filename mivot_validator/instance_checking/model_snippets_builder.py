"""
Created on 19 Apr 2023

use a modified version of the snippet builder to generate snippets for all the objectTypes
of a VODML model

@author: julien abid
"""
import os

from mivot_validator.instance_checking.snippet_builder import Builder
from mivot_validator.utils.xml_utils import XmlUtils


class ModelBuilder(Builder):
    def __init__(self, vodml_path, output_dir=os.getcwd() + "/../tmp_snippets/"):
        self.model_name = os.path.basename(vodml_path).split('.')[0].split('_')[0].split('-')[0].lower()
        super().__init__(self.model_name, "", vodml_path, output_dir)

    def build(self):
        """
        Build one snippet for all the dataType/objectType which are not abstract,
        found in the VODML model
        """
        for ele in self.vodml.xpath(f'.//objectType'):
            if ele.get("abstract") == "true":
                continue
            for tags in ele.getchildren():
                self.class_name = tags.text
                if tags.tag != "vodml-id":
                    continue
                self.build_object(ele, "", True, True)

        return True

    def build_object(self, ele, role, root, aggregate):
        """
        Build a MIVOT instance from a VOMDL element
        :ele: VODML representation of the class to be mapped
        :role: VODML role to be affected to the built instance
        :aggregate: If False, all componentsfound out in the VODML element are added to the enclosing instance
                    (in that case of inheritance reconstruction) . Otherwise, those components are
                    enclosed in an INSTANCE (composition case)
        """

        print(f"build object with role={role} within the class {self.class_name}")
        for tags in list(ele):
            if tags.tag == "constraint":
                self.constraints.add_constraint(tags)
                break
        for tags in list(ele):
            print(f"   TAG {tags.tag}")
            if tags.tag == "vodml-id":
                if root is True:
                    output_dir = self.output_dir + self.model_name + "/"

                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)

                    self.outputname = os.path.join(
                        output_dir,
                        self.model_name + "." + tags.text + ".xml"
                    )

                    print(self.outputname)

                    print(f"opening {self.outputname}")
                    self.output = open(self.outputname, "w")

                print(f"== build {tags.text}")
                if aggregate is True:
                    dmid = ""
                    if role == "coords:Coordinate.coordSys":
                        self.write_out(
                            f'<!-- The Coordinate system can be pushed up to the GLOBALS and replaced here with '
                            f'<REFERENCE dmref="SOME_REF" dmrole="{role}" />">-->')
                        dmid = 'dmid="PUT_AN_ID_HERE"'
                    self.write_out(f'<INSTANCE {dmid} dmrole="{role}" dmtype="{self.model_name}:{tags.text}">')
            elif tags.tag == "extends":
                self.addExtend(tags)
            elif tags.tag == "reference":
                self.addReference(tags)
            elif tags.tag == "composition":
                self.addComposition(tags)
            elif tags.tag == "attribute":
                self.addAttribute(tags)
            elif tags.tag == "description":
                if aggregate is True:
                    self.write_out(f'<!-- {tags.text}" -->')
            elif tags.tag == "multiplicity":
                int(tags.xpath(".//maxOccurs")[0].text)

        if aggregate is True:
            self.write_out("</INSTANCE>")

        if root is True:
            self.output.close()
            XmlUtils.xmltree_to_file(XmlUtils.xmltree_from_file(self.outputname), self.outputname)
