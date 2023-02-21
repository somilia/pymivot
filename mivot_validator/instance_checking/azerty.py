'''
Created on 21 Feb 2023

@author: laurentmichel
'''
import os
from astropy.io.votable import parse
from mivot_validator.instance_checking.xml_interpreter.model_viewer import ModelViewer
from mivot_validator.instance_checking.instance_checker import InstanceChecker

if __name__ == '__main__':
    data_path = os.path.dirname(os.path.realpath(__file__))
    votable_path = os.path.join(data_path, "../../tests/data/gaia_luhman16.xml")
    votable = parse(votable_path)
    
    mviewer = None
    for resource in votable.resources:
        mviewer = ModelViewer(resource, votable_path=votable_path)
        mviewer.connect_table(None)
        mviewer.get_next_row() 
        model_view = mviewer.get_model_view(resolve_ref=True)
        for instance in model_view.xpath(".//INSTANCE"):
            print(f'CHECKING: instance{instance.get("dmtype")}')
            InstanceChecker.check_class_validity(instance)

