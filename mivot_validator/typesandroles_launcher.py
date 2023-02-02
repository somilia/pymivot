'''
Created on 23 Jun 2022

@author: laurentmichel
'''
import sys
from .dmtypes_and_role_checker import DmTypesAndRolesChecker

def main():
    """
    Package launcher (script)
    """
    if len(sys.argv) != 2 :
        print("USAGE: types-and-roles-validate [path]")
        print("   Validate all dmtypes and dmroles")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)
        
    types_and_role_checker = DmTypesAndRolesChecker()
    if types_and_role_checker.validate_mivot(sys.argv[1]) is True:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()