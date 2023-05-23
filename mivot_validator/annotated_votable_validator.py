"""
Created on 2022/07/01

@author: laurentmichel
"""
import os
import ssl
from mivot_validator.xml_validator import XMLValidator
from mivot_validator import logger

ssl._create_default_https_context = ssl._create_unverified_context


class AnnotatedVOTableValidator:
    """
    Validate tool for annotated VOTable
    Operate 2 separate validations
    - One for the VOTable
    - One for the MIVOT annotations

    See the mivot_launcher to get how to use it
    """

    # VOtable schema
    # MIVOT schema
    votable_validator = XMLValidator("http://www.ivoa.net/xml/VOTable/v1.3")
    vodml_validator = XMLValidator(
        "https://raw.githubusercontent.com/ivoa-std/"
        "ModelInstanceInVot/master/schema/xsd/mivot-v1.0.xsd"
    )

    def validate(self, data_path):
        """
        Validate the content of data_path.
        If data_path is a directory, all its direct content is evaluated and
        the method returns false at the first XML file not validating
        :param data_path: file or directory path to be evaluated
        :type data_path: string
        :return: true all files validate
        :rtype: boolean
        """

        # Check that the path exist
        if os.path.exists(data_path) is False:
            logger.error(f"Path {data_path} does not exist")
            return False

        # Process the whole directory content
        if os.path.isdir(data_path):
            files = os.listdir(data_path)
            for sample_file in files:
                file_path = os.path.join(data_path, sample_file)
                if os.path.isdir(file_path):
                    continue
                if self.__is_xml(file_path) is True:
                    if self.__validate_file(file_path) is False:
                        return False
            return True

        # Process one single
        return self.__validate_file(data_path)

    def __validate_file(self, file_path):
        """
        Validate one XML file.
        2 step validation : VOTable first and then MIVOT
        :param file_path: file to be evaluated
        :type file_path: string
        :return: true all files validate
        :rtype: boolean
        """

        # non XML files are considered as non valid
        if self.__is_xml(file_path) is False:
            logger.error(f"File {file_path} does not look like XML")
            return False

        # Get the filename for the log messages
        file_name = os.path.basename(file_path)
        logger.info(f"Validate file {file_name}")
        logger.info("- Validate against VOTable/v1.3")
        # Validate the VOTable
        if (
            AnnotatedVOTableValidator.votable_validator.validate_file(
                file_path, verbose=False
            )
            is False
        ):
            AnnotatedVOTableValidator.votable_validator.validate_file(
                file_path, verbose=True
            )
            logger.error("Not a valid VOTable")
            return False
        logger.info("- passed")
        # and then validate the annotations
        logger.info("- Validate against MIVOT")
        retour = self.validate_mivot(file_path)
        if retour is True:
            logger.info(f"{file_name} is a valid annotated VOTable")
        return retour

    def validate_mivot(self, file_path):
        """
        Validate MIVOT block in one XML file.
        :param file_path: file to be evaluated
        :type file_path: string
        :return: true all files validate
        :rtype: boolean
        """
        # non XML files are considered as non valid
        if self.__is_xml(file_path) is False:
            logger.error("File {file_path} does not look like XML")
            return False
        if (
            AnnotatedVOTableValidator.vodml_validator.validate_file(
                file_path, verbose=False
            )
            is False
        ):
            AnnotatedVOTableValidator.vodml_validator.validate_file(
                file_path, verbose=True
            )
            logger.error("MIVOT annotations are not valid")
            return False
        return True

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
