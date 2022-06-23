'''
Created on 23 Jun 2022

@author: laurentmichel
'''
import sys
from .annotated_votable_validator import AnnotatedVOTableValidator

if __name__ == '__main__':
    """
    Package launcher (script)
    """
    if len(sys.argv) != 2 :
        print("USAGE: mivot-validate [path]")
        print("   path: either a simple file or a directory")
        print("         all directory files matching *.vot or *.xml are validatedß")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)
        
    annotated_votable_validator = AnnotatedVOTableValidator()
    if annotated_votable_validator.validate(sys.argv[1]) is True:
        sys.exit(0)
    else:
        sys.exit(1)
