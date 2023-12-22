"""
Created on 23 Jun 2022

@author: laurentmichel
"""
import sys
from pymivot.validator.mivot_validator.annotated_votable_validator import AnnotatedVOTableValidator


def main():
    """
    Package launcher (script)
    """
    if len(sys.argv) != 2:
        print("USAGE: mivot-mapping-validate [path]")
        print("   Validate XML files against  MIVOT schemas")
        print("   path: either a simple file or a directory")
        print("         all directory XML files are validated")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)

    annotated_votable_validator = AnnotatedVOTableValidator()
    if annotated_votable_validator.validate_mivot(sys.argv[1]) is True:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
