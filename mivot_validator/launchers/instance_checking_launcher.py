'''
Created on 23 Jun 2022

@author: laurentmichel
'''
import sys
import os
from astropy.io.votable import parse
from mivot_validator.instance_checking.xml_interpreter.model_viewer import ModelViewer
from mivot_validator.instance_checking.instance_checker import InstanceChecker

def main():
    """
    Package launcher (script)
    """
    if len(sys.argv) != 2 :
        print("USAGE: mivot-instance-validate [path]")
        print("   Validate the mapped instances against the VODML definitoins")
        print("   path: path to the mapped VOTable to be checked")
        print("   exit status: 0 in case of success, 1 otherwise")
        sys.exit(1)
        
    votable_path = sys.argv[1]
    votable = parse(votable_path)
    
    mviewer = None
    if len(votable.resources) != 1 :
        print("VOTable with more than one resource are not supported yet")
        sys.exit(1)
        
    # Connect the model viewer to the first table of the first resource    
    for resource in votable.resources:
        if len(resource.tables) != 1 :
            print(f"Resources with more than one table are not supported yet: {len(resource.tables)} tables found")
            sys.exit(1)
        # The model viewer is a module able to provide a model view on data
        mviewer = ModelViewer(resource, votable_path=votable_path)
        mviewer.connect_table(None)
        # Seek the first data row
        mviewer.get_next_row()
        # and get its model view 
        # The references are resolved in order to be able to check their counterparts
        model_view = mviewer.get_model_view(resolve_ref=True)
        # Validate all instances  on which the table data are mapped
        InstanceChecker._clean_tmpdata_dir()
        for instance in model_view.xpath(".//INSTANCE"):
            print(f'CHECKING: instance {instance.get("dmtype")}')
            InstanceChecker.check_instance_validity(instance)

if __name__ == '__main__':
    main()