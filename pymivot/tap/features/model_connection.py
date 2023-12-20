import os
import lxml.etree as ET

from pymivot.tap.exceptions.exceptions import DmroleInvalidException


class ModelConnection:

    def __init__(self, vodml_path, output_dir):
        self.model_name = (
            os.path.basename(vodml_path)
            .split(".")[0]
            .split("_")[0]
            .split("-")[0]
            .lower()
        )
        self.mivot_check_env(vodml_path)
        self.vodml = ET.parse(vodml_path)

    def mivot_check_env(self, vodml_path):
        """
        Check if the path vodlm_path exist and is writable
        """
        if not os.path.exists(vodml_path):
            raise Exception(f"File {vodml_path} does not exist")
        if not os.access(vodml_path, os.W_OK):
            raise Exception(f"File {vodml_path} is not writable")

    def is_dmrole_valid(self, dmtype_candidate, dmrole_candidate):
        """
        Check if the dmrole_candidate is a dmrole in the VODML model
        """
        candidate = f"{dmtype_candidate}.{dmrole_candidate}"
        for ele in self.vodml.xpath(".//vodml-id"):
            if '.' in ele.text.lower():
                if ele.text.lower().split('.', 1)[1] == candidate.lower():
                    print(f"{dmrole_candidate} is a dmrole")
                    return True
        raise DmroleInvalidException(f"{dmrole_candidate} is not a dmrole of {dmtype_candidate} in the VODML model {self.model_name}")
