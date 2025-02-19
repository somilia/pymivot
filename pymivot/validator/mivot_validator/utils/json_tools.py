"""
Created on Jan 11, 2021

@author: laurentmichel
"""

from pymivot.validator.mivot_validator.instance_checking.xml_interpreter.vocabulary import Ele


class JsonTools:
    """
    classdocs
    """

    @staticmethod
    def remove_key(dictionary, key):
        """
        remove a key from a dictionary
        """
        if isinstance(dictionary, dict):
            return JsonTools.remove_dict_key(dictionary, key)
        if isinstance(dictionary, list):
            return JsonTools.remove_list_key(dictionary, key)
        raise Exception("Unsupported type")

    @staticmethod
    def remove_dict_key(dictionary, key):
        """
        {key: {"A": "a", "B": "b"}}
            --> {"A": "a", "B": "b"}
        {key: [{"A1": "a", "B1": "b"}, {"A2": "a", "B2": "b"}]}
            --> [{"A1": "a", "B1": "b"}, {"A2": "a", "B2": "b"}]
        """
        if key not in dictionary:
            return dictionary
        if isinstance(dictionary[key], dict):
            return dictionary[key]
        if isinstance(dictionary[key], list):
            return dictionary[key]
        raise Exception("Unsupported type")

    @staticmethod
    def remove_list_key(dictionary, key):
        """
        [{key: {"A1": "a", "B1": "b"}}]
            --> [{"A1": "a", "B1": "b"}]
        [{key: [{"A1": "a", "B1": "b"}, {"A2": "a", "B2": "b"}]}]
            --> [{"A1": "a", "B1": "b"}, {"A2": "a", "B2": "b"}]
        """
        retour = []
        for item in dictionary:
            content = JsonTools.remove_dict_key(item, key)
            if isinstance(content, dict):
                retour.append(content)
            elif isinstance(content, list):
                retour = content
            else:
                raise Exception("Unsupported type")

        return retour

    @staticmethod
    def is_join(input_list):
        """
        Check if input_list contains a join key
        """
        if isinstance(input_list, list):
            for item in input_list:
                if Ele.JOIN in item.keys():
                    return True
        if isinstance(input_list, dict):
            for key in input_list.keys():
                if Ele.JOIN == key:
                    return True
        return False
