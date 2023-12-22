"""
Created on 21 Feb 2023

@author: laurentmichel
"""
import os
import shutil
import urllib.request

from pymivot.validator.mivot_validator.utils.xml_utils import XmlUtils
from pymivot.validator.mivot_validator.instance_checking.inheritance_checker import InheritanceChecker
from pymivot.validator.mivot_validator.instance_checking.snippet_builder import Builder

tmp_data_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "tmp_snippets"
)
vodml_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "vodml")

# types to be ignored for now
inheritence_tree = {}
ivoa_types = ["ivoa:RealQuantity", "ivoa:IntQuantity"]


class CheckFailedException(Exception):
    pass


class InstanceChecker:
    """
    API operating the validation of mapped instances against the VODML definition
    - all ATTRIBUTE/COLLECTION/INSTANCE children of the mapped instance must be
      referenced in the VODML with the same dmrole and the same dmtype.
    - The dmtype checking takes into account the inheritance
    - The mapped instances must not necessary host all the components declared in the VODML
    - All the components hosted by the mapped instances must be compliant with the VODML

    The VODML files are stored locally for the moment
    """

    inheritence_tree = {"meas:Measure": ["mango:extmeas.PhotometricMeasure"]}

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

            vodml_filename = InstanceChecker._get_model_location(model)
            builder = Builder(
                model,
                dmtype,
                # "Property",
                vodml_filename,
                tmp_data_path,
            )
            # build the XML snippet and store it on disk
            builder.build()
            InstanceChecker._build_inheritence_graph(vodml_filename)
        else:
            print(f"-> snippet for class {dmtype} already in the cache")

        return XmlUtils.xmltree_from_file(filepath)

    @staticmethod
    def _clean_tmpdata_dir():
        for filename in os.listdir(tmp_data_path):
            file_path = os.path.join(tmp_data_path, filename)
            if filename.endswith(".xml") and os.path.isfile(file_path):
                os.unlink(file_path)

    @staticmethod
    def _get_vodmlid(vodmlid, model_name):
        if ":" in vodmlid:
            return f"{vodmlid}"
        return f"{model_name}:{vodmlid}"

    @staticmethod
    def _get_model_location(model):
        """
        Store locally the VODML file in the local cache
        """
        if model.lower() == "meas":
            vodml_filename = "Meas-v1.vo-dml.xml"
        elif model.lower() == "coords":
            vodml_filename = "Coords-v1.0.vo-dml.xml"
        elif model.lower() == "phot":
            vodml_filename = "Phot-v1.vodml.xml"
        elif model.lower() == "ivoa":
            vodml_filename = "IVOA-v1.vo-dml.xml"
        elif model.lower() == "mango":
            vodml_filename = "mango.vo-dml.xml"
        else:
            raise CheckFailedException(f"Model {model} not supported yet")

        output_path = os.path.join(tmp_data_path, vodml_filename)
        if os.path.exists(output_path) is False:
            url = f"https://ivoa.net/xml/VODML/{vodml_filename}"
            print(f"-> downloading {url}")
            try:
                urllib.request.urlretrieve(url, output_path)
            except:
                print(f"-> download failed, try to copy from  {vodml_path}")
                shutil.copy(os.path.join(vodml_path, vodml_filename), tmp_data_path)
        return output_path

    @staticmethod
    def _build_inheritence_graph(vodml_filepath):
        """
        Build a map of the inheritance links.
        This is necessary to resolve cases where the model refer to abstract types
        and the annotation uses concrete types (sub-types)
        """
        vodml_tree = XmlUtils.xmltree_from_file(vodml_filepath)
        graph = {}
        for ele in vodml_tree.xpath("./name"):
            model_name = ele.text
        print(f"   Build inheritence tree for model {model_name}")

        # Build a map superclass : [sublcasses]
        # No distinctions between objecttypeand datatypes
        # MIVOT does not make any difference
        # the vodml)id are unique within the scope of the whole model
        for ele in vodml_tree.xpath("./dataType"):
            for tags in ele.getchildren():
                if tags.tag == "vodml-id":
                    sub_class = model_name + ":" + tags.text
                for ext in ele.xpath("./extends/vodml-ref"):
                    super_class = ext.text
                    if super_class not in graph:
                        graph[super_class] = []
                    if sub_class not in graph[super_class]:
                        graph[super_class].append(sub_class)

        for ele in vodml_tree.xpath("./objectType"):
            for tags in ele.getchildren():
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
            for val in deep_tree[key]:
                if val not in graph[key]:
                    graph[key].append(val)
        for key in graph:
            if key not in InstanceChecker.inheritence_tree:
                InstanceChecker.inheritence_tree[key] = graph[key]
            else:
                InstanceChecker.inheritence_tree[key] = (
                    InstanceChecker.inheritence_tree[key] + graph[key]
                )
        # ivoa model is not parsed yet....
        if "ivoa:Quantity" not in InstanceChecker.inheritence_tree:
            InstanceChecker.inheritence_tree["ivoa:Quantity"] = ivoa_types
        # Cross model inheritance not supported yet
        if "meas:Measure" in InstanceChecker.inheritence_tree:
            InstanceChecker.inheritence_tree["meas:Measure"].append(
                "mango:extmeas.PhotometricMeasure"
            )

        return graph

    @staticmethod
    def _check_attribute(attribute_etree, vodml_instance):
        """
        checks that the MIVOT representation of the attribute matches the model definition

        parameters
        ----------
        attribute_etree: etree
            MIVOT representation of the attribute
        vodml_instance: etree
            VODML serialization of that attribute
        return
        ------
            boolean
        """
        for child in vodml_instance.xpath("./ATTRIBUTE"):
            if child.get("dmrole") == attribute_etree.get("dmrole") and child.get(
                "dmtype"
            ) == attribute_etree.get("dmtype"):
                return True
        return False

    @staticmethod
    def _check_collection(collection_etree, vodml_instance):
        """
        checks that the MIVOT representation of the collection matches the model definition

        parameters
        ----------
        collection_etree: etree
            MIVOT representation of the collection
        vodml_instance: etree
            VODML serialization of that collection
        return
        ------
            a documented  exception in case of failure
        """

        collection_role = collection_etree.get("dmrole")

        # Checks that collection items have all the same type
        item_type = ""
        for item in collection_etree.xpath("./*"):
            mivot_item_type = item.get("dmtype")
            checker = InheritanceChecker(InstanceChecker.inheritence_tree)
            if item_type != "" and not checker.check_inheritance(
                mivot_item_type, item_type
            ):
                raise CheckFailedException(
                    f"Collection with dmrole={collection_role} has items with different dmtypes "
                )
            item_type = mivot_item_type

        # check that the mapped collection item have the type defined in the model
        role_found = False

        for vodml_child in vodml_instance.xpath("./COLLECTION"):
            if vodml_child.get("dmrole") == collection_etree.get("dmrole"):
                role_found = True
                # Get the item type as defined by vodml
                for vodml_item in vodml_child.xpath("./*"):
                    vodml_type = vodml_item.get("dmtype")
                    break
                # Get the item type as used by mivot
                for item in collection_etree.xpath("./*"):
                    mivot_item_type = item.get("dmtype")
                    if (
                        mivot_item_type not in ivoa_types
                        and mivot_item_type != vodml_type
                        and (
                            vodml_type not in InstanceChecker.inheritence_tree
                            or mivot_item_type
                            not in InstanceChecker.inheritence_tree[vodml_type]
                        )
                    ):
                        raise CheckFailedException(
                            f"Collection with dmrole={collection_role} "
                            f"has items with prohibited types ({mivot_item_type}) "
                            f"instead of expected {vodml_type} "
                        )
                    for item in collection_etree.xpath("./*"):
                        if item.tag == "INSTANCE":
                            InstanceChecker.check_instance_validity(item)
                    return

        if role_found is False:
            raise CheckFailedException(
                f"No collection with dmrole {collection_role} "
                f"in object type {vodml_instance.getroot().get('dmtype')}"
            )

    @staticmethod
    def _check_membership(actual_instance, enclosing_vodml_instance):
        """
        Checks that the MIVOT component is a component of the VODML class

        parameters
        ----------
        actual_instance: etree
            MIVOT instance
        enclosing_vodml_instance: etree
            VODML class supposed to enclose the actual instance
        return
        -------
            a documented exception ins case of failure
        """
        actual_role = actual_instance.get("dmrole")
        for vodml_instance in enclosing_vodml_instance.getroot().xpath("./*"):
            if vodml_instance.get("dmrole") == actual_role:
                actual_type = actual_instance.get("dmtype")
                vodml_type = vodml_instance.get("dmtype")
                if actual_type == vodml_type:
                    return
                # Sort of ad_hoc patch meanwhile ivoa DM is properly supported
                if actual_type == "ivoa:RealQuantity" and vodml_type == "ivoa:Quantity":
                    return
                if (
                    vodml_type in InstanceChecker.inheritence_tree
                    and actual_type in InstanceChecker.inheritence_tree[vodml_type]
                ):
                    print(f"-> found that {actual_type} inherits from {vodml_type}")
                    return
                raise CheckFailedException(
                    f"Object type {enclosing_vodml_instance.getroot().get('dmtype')} "
                    f"has no component with dmrole={actual_role} and dmtype={actual_type} "
                    f"type should be {vodml_type}"
                )
        raise CheckFailedException(
            f"dmrole {actual_role} not found in "
            f"object type {enclosing_vodml_instance.getroot().get('dmtype')}"
        )

    @staticmethod
    def check_instance_validity(instance_etree):
        """
        Public method. The only one meant to be used from from outside
        Checks that instance_etree is compliant with the model it refers to

        parameters
        ----------
        instance_etree: etree
            MIVOT instance to be checked
        return
        -------
            a documented exception ins case of failure
        """
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

                # ivao:Quantity are complex types that can be serialized as ATTRIBUTE.
                # This is an exception
                if (
                    child.get("dmtype") not in ivoa_types
                    and InstanceChecker._check_attribute(child, vodml_instance) is False
                ):
                    message = (
                        f"cannot find attribute with dmrole={dmrole} "
                        f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                    )
                    raise CheckFailedException(message)
                print(
                    f'VALID: attribute with dmrole={child.get("dmrole")} '
                    f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                )
            elif child.tag == "INSTANCE":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                checked_roles.append(child.get("dmrole"))

                if InstanceChecker.check_instance_validity(child) is False:
                    message = (
                        f"cannot find instance with dmrole={dmrole} "
                        f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                    )
                    raise CheckFailedException(message)
                InstanceChecker._check_membership(child, vodml_instance)
                print(
                    f"VALID: instance with dmrole={dmrole} "
                    f'dmtype={child.get("dmtype")} in complex type {dmtype}'
                )

            elif child.tag == "COLLECTION":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                checked_roles.append(child.get("dmrole"))

                if InstanceChecker._check_collection(child, vodml_instance) is False:
                    message = (
                        f"cannot find collection with dmrole={dmrole} "
                        f"in complex type {dmtype}"
                    )
                    raise CheckFailedException(message)
                print(
                    f"VALID: collection with dmrole={dmrole} "
                    f"in complex type {dmtype}"
                )
            elif child.tag == "REFERENCE":
                dmrole = child.get("dmrole")
                if dmrole in checked_roles:
                    raise CheckFailedException(f"Duplicated dmrole {dmrole}")
                print(f"SKIPPED: Reference to instance with dmrole={dmrole}")

            else:
                raise CheckFailedException(f"unsupported tag {child.tag}")
        return True
