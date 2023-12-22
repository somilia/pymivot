import os
import lxml.etree as ET

from pymivot.tap.exceptions.exceptions import DmroleInvalidException, DmtypeInvalidException


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
        self.dmtype_dmrole_mango = self.get_dmtypes_mango_model()

    def mivot_check_env(self, vodml_path):
        """
        Check if the path vodlm_path exist and is writable
        """
        if not os.path.exists(vodml_path):
            raise Exception(f"File {vodml_path} does not exist")
        if not os.access(vodml_path, os.W_OK):
            raise Exception(f"File {vodml_path} is not writable")

    def get_dmtypes_mango_model(self):
        dmtypes_mango_model = {}
        for ele in self.vodml.xpath(".//vodml-id"):
            if '.' in ele.text.lower():
                if '.' in ele.text.lower().split('.', 1)[1]:
                    if ele.text.lower().split('.', 2)[1] not in dmtypes_mango_model.keys():
                        dmtypes_mango_model[ele.text.lower().split('.', 2)[1]] = [ele.text.lower().split('.', 2)[2]]
                    else:
                        dmtypes_mango_model[ele.text.lower().split('.', 2)[1]].append(ele.text.lower().split('.', 2)[2])

        return dmtypes_mango_model

    def is_dmtype_valid(self, dmtype_candidate):
        if dmtype_candidate in self.dmtype_dmrole_mango.keys():
            return True
        else:
            return False

    def is_dmrole_valid(self, dmtype_candidate, dmrole_candidate):
        """
        Check if the dmrole_candidate is a dmrole in the VODML model

        Parameters
        ----------
        dmtype_candidate : str
            The dmtype candidate
        dmrole_candidate : str
            The dmrole candidate

        Returns
        -------
        bool
            True if the dmrole_candidate is a dmrole in the VODML model, False otherwise

        Raises
        ------
        DmroleInvalidException
            If the dmrole_candidate is not a dmrole in the VODML model
        DmtypeInvalidException
            If the dmtype_candidate is not a dmtype in the VODML model
        """

        candidate = f"{dmtype_candidate}.{dmrole_candidate}".lower()
        if self.is_dmtype_valid(dmtype_candidate.lower()):
            if dmrole_candidate.lower() in self.dmtype_dmrole_mango[dmtype_candidate.lower()]:
                print(f"{candidate} is a valid dmrole")
                return True
            else:
                raise DmroleInvalidException(f"{dmrole_candidate} is not a dmrole of {dmtype_candidate} in the VODML model {self.model_name}")
        else:
            raise DmtypeInvalidException(f"{dmtype_candidate} is not a dmtype of {self.model_name}")
        # dmtype_exists = False
        # for ele in self.vodml.xpath(".//vodml-id"):
        #     if '.' in ele.text.lower():
        #         if ele.text.lower().split('.', 2)[1] == dmtype_candidate.lower():
        #             if ele.text.lower().split('.', 1)[1] == candidate:
        #                 print(f"{candidate} is a valid dmrole")
        #                 return True
        #             dmtype_exists = True
        # if dmtype_exists:
        #     raise DmroleInvalidException(f"{dmrole_candidate} is not a dmrole of {dmtype_candidate} in the VODML model {self.model_name}")
        # else:
        #     raise DmtypeInvalidException(f"{dmtype_candidate} is not a dmtype of {self.model_name}")
