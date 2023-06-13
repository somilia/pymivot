"""
Created on 30 May 2023

@author: julien abid
"""


class InheritanceChecker:
    """
    classdocs
    """

    def __init__(self, tree):
        """
        Constructor
        """
        self.tree = tree

    def get_inheritance(self, class_name):
        """
        Get the inheritance of an inheritance tree for a given class
        """
        keys = []
        for k, v in self.tree.items():
            if class_name in v:
                keys.append(k)
        return keys

    def check_inheritance(self, first_class, second_class):
        """
        Check if two classes are in inheritance relation
        """

        if first_class == second_class:
            return True

        inheritance_first = self.get_inheritance(first_class)
        inheritance_second = self.get_inheritance(second_class)

        for el in inheritance_first:
            if el in inheritance_second:
                return True

        return False
