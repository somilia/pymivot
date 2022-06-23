'''
Created on 2021/07/01

@author: laurentmichel
'''

import xmlschema
from mivot_validator import logger


class XMLValidator:
    """
    Convenient wrapper for the xmlschema validator 
    TODO: managing the verbosity 
    """
    def __init__(self, xsd_path):
        logger.info("Using schema %s", xsd_path)
        # Schema against which data are validated
        self.xmlschema = xmlschema.XMLSchema11(xsd_path)

    def validate_file(self, xml_path: str, verbose=False) -> bool:
        """
        Validate one file
        """
        if verbose is True:
            try :
                self.xmlschema.validate(xml_path)
                return True
            except Exception as excep:
                logger.error(f"validation failed {excep}")
                return False
        else :
            return self.xmlschema.is_valid(xml_path)

        
    def validate_string(self, xml_string: str, verbose=False) -> bool:
        """
        Validate one XML string
        """
        if verbose is True:
            try :
                self.xmlschema.validate(xml_string)
                return True
            except Exception as excep:
                logger.error(f"validation failed {excep}")
                return False
        else :
            return self.xmlschema.is_valid(xml_string)
        
