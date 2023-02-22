'''
Created on 21 Feb 2023

@author: laurentmichel
'''
import os
from mivot_validator.utils.xml_utils import XmlUtils
from mivot_validator.instance_checking.snippet_builder import Builder

tmp_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "tmp_snippets")
vodml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "vodml")

# must be built from VODML in a later version
inheritence_tree = {
    "coords:Point": ["coords:LonLatPoint"],
    "ivoa:Quantity": ["ivoa:RealQuantity"],
    "meas:Symmetrical": ["meas:Asymmetrical3D"],
    "meas:Error": ["meas:Asymmetrical2D"],
    }
inheritence_tree = {}

class CheckFailedException(Exception):
    pass

class InstanceChecker(object):
    '''
    API operating the validation of mapped instances against the VODML definition
    - all ATTRIBUTE/COLLECTION/INSTANCE children of the mapped instance must be
      referenced in the VODML with the same dmrole and the same dmtype.
    - The dmtype checking takes into account the inheritance
    - The mapped instances must not necessary host all the components declared in the VODML
    - All the components hosted by the mapped instances must be compliant with the VODML
    
    The VODML files are stored locally for the moment
    '''

    inheritence_tree = {}

    @staticmethod
    def _get_vodml_class_tree(model, dmtype):
        """
        Extract from the VODML file the object to be checked 
        Store first on disk a VODML representation of the searched object type
        and then works with that XML snippet
        
        Only Meas/Coords/PhotDM are supported yet
        
        parameters
        ----------
        model: string
            model short name as defined by the VODML 
        dmtype: string
            type of the model component to be checked
            
        return
        ------
        The etree serialisation of the XML snippet
        """
        filepath = os.path.join(tmp_data_path, f"{model}:{dmtype}")
        filepath = filepath.replace(":", ".") + ".xml"

        if os.path.exists(filepath) is False:
            print(f"-> build snippet for class {model}:{dmtype}")

            if model == "meas":
                vodml_filename = os.path.join(vodml_path, "Meas-v1.vo-dml.xml")
            elif model == "coords":
                vodml_filename = os.path.join(vodml_path, "Coords-v1.0.vo-dml.xml")
            elif model == "Phot":
                vodml_filename = os.path.join(vodml_path, "Phot-v1.1.vodml.xml")
            
            builder = Builder(
                model,
                dmtype,
                vodml_filename,
                tmp_data_path
            )
            # build the XML snippet and store it on disk
            builder.build()
            CheckFailedException._build_inheritence_graph(vodml_filename)
        else:
            print(f"-> snippet for class {dmtype} already in the cache")
            
        return XmlUtils.xmltree_from_file(filepath)

    @staticmethod
    def _build_inheritence_graph(vodml_filepath):
        vodml_tree = XmlUtils.xmltree_from_file(vodml_filepath)
        graph = {}
        for ele in vodml_tree.xpath(f'./name'):
            model_name = ele.text
            
        # Build a map superclass : [sublcasses]
        # No distinctions between objecttypeand datatypes
        # MIVOT does not make any difference 
        # the vodml)id are unique within the scope of the whole model
        for ele in vodml_tree.xpath(f'./dataType'):
            for tags in ele.getchildren  (): 
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)
                        
        for ele in vodml_tree.xpath(f'./objectType'):
            for tags in ele.getchildren  (): 
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)
        #
        # We have inheritance with multiple levels (A->B->C)
        # In such a case we must consider (in term of validation) that C extends A as well 
        # This the purpose of the code below.
        # {A: [B, C, D]  C:[X, Y]} --> {A: [B, C, D, X, Y],  C:[X, Y]}  
        deep_tree = {}
        for superclass, subclasses in graph.items():
            for subclass in subclasses:
                if subclass in graph:
                    if superclass not in deep_tree:
                        deep_tree[superclass] = []
                    for sc in graph[subclass]:
                        if sc not in deep_tree[superclass]:
                            deep_tree[superclass].append(sc)  

        for key in deep_tree:
            for val in  deep_tree[key]:
                if val not in graph[key]:
                    graph[key].append(val)  
               
        InstanceChecker.inheritence_tree = graph

    @staticmethod
    def _check_attribute(attribute_etree, vodml_instance):
        for child in vodml_instance.xpath("./ATTRIBUTE"):
            if( child.get("dmrole") == attribute_etree.get("dmrole") and 
                child.get("dmtype") == attribute_etree.get("dmtype")
                ):
                return True
        return False
    
    @staticmethod
    def _check_collection(collection_etree, vodml_instance):
        collection_role = collection_etree.get("dmrole")
        item_type = ""
        for item in collection_etree.xpath("./*"):
            local_item_type = item.get("dmtype") 
            if (item_type != "" and item_type != local_item_type):
                raise CheckFailedException(f"Collection with dmrole={collection_role} has items with different dmtypes ")
            item_type = local_item_type
        
        for child in vodml_instance.xpath("./COLLECTION"):
            if child.get("dmrole") == collection_etree.get("dmrole"):
                for item in child.xpath("./*"):
                    local_item_type = item.get("dmtype")
                    if  local_item_type != item_type:
                        raise CheckFailedException(f"Collection with dmrole={collection_role} "
                                                   f"has items with prohibited types ({local_item_type} "
                                                   f"instead of expected {item_type} ")
                return True
        raise CheckFailedException(f"No collection with dmrole {collection_role} in object type {vodml_instance.getroot().get('dmtype')}")

    @staticmethod
    def _check_membership (actual_instance, enclosing_vodml_instance):   
        actual_role = actual_instance.get("dmrole")
        for vodml_instance in enclosing_vodml_instance.getroot().xpath("./*"):
            if vodml_instance.get("dmrole") == actual_role:
                actual_type = actual_instance.get("dmtype")
                vodml_type = vodml_instance.get("dmtype")
                if actual_type == vodml_type:
                    return
                if (vodml_type in InstanceChecker.inheritence_tree and 
                    actual_type in InstanceChecker.inheritence_tree[vodml_type]
                    ):
                    print(f"-> found that {actual_type} inherits from {vodml_type}")
                    return
                raise CheckFailedException(f"Object type {enclosing_vodml_instance.getroot().get('dmtype')} "
                                           f"has no component with dmrole={actual_role} and dmtype={actual_type} "
                                           f"type should be {vodml_type}")

        raise CheckFailedException(f"dmrole {actual_role} not found in object type {enclosing_vodml_instance.getroot().get('dmtype')}")
            
    @staticmethod
    def check_instance_validity(instance_etree):
        checked_roles = []
        dmtype = instance_etree.get("dmtype")
        eles = dmtype.split(":")
        print(f"-> check class {eles[0]}:{eles[1]}")
        if eles[0] == "ivoa":
            print("-> IVOA/ see later")
            return True
        vodml_instance = InstanceChecker._get_vodml_class_tree(eles[0], eles[1])
        
        for child in instance_etree.xpath("./*"):
            if child.tag == "ATTRIBUTE":
                InstanceChecker._check_membership(child, vodml_instance)
                
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                checked_roles.append(child.get("dmrole"))
                
                if InstanceChecker._check_attribute(child, vodml_instance) is False:
                    message = (f'cannot find attribute with dmrole={dmrole} '
                               f'dmtype={child.get("dmtype")} in complex type {dmtype}')
                    raise CheckFailedException(message)
                else :
                    print(f'VALID: attribute with dmrole={child.get("dmrole")} '
                          f'dmtype={child.get("dmtype")} in complex type {dmtype}')
            elif child.tag == "INSTANCE":
                InstanceChecker._check_membership(child, vodml_instance)
                
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                checked_roles.append(child.get("dmrole"))
                
                if InstanceChecker.check_instance_validity(child) is False:
                    message = (f'cannot find instance with dmrole={dmrole} '
                               f'dmtype={child.get("dmtype")} in complex type {dmtype}')
                    raise CheckFailedException(message)
                else :
                    print(f'VALID: instance with dmrole={dmrole} '
                          f'dmtype={child.get("dmtype")} in complex type {dmtype}')

            elif child.tag == "COLLECTION":
                
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                checked_roles.append(child.get("dmrole"))
                
                if InstanceChecker._check_collection(child, vodml_instance) is False:
                    message = (f'cannot find collection with dmrole={dmrole} '
                               f'in complex type {dmtype}')
                    raise CheckFailedException(message)
                else :
                    print(f'VALID: collection with dmrole={dmrole} '
                          f'in complex type {dmtype}')
            else:
                raise CheckFailedException(f'unsupported tag {child.tag}')
        return True
    