"""
Created on 30 May 2023

@author: julien abid
"""


class InheritanceChecker:
    """
    classdocs
    """

    @staticmethod
    def get_inheritance(tree, class_name):
        """
        Get the inheritance of an inheritance tree for a given class
        """
        for k, v in tree.items():
            if class_name in v:
                return k
        return []

    @staticmethod
    def check_inheritance(tree, first_class, second_class):
        """
        Check if two classes are in inheritance relation
        """

        if first_class == second_class:
            return True

        inheritance_first = InheritanceChecker.get_inheritance(tree, first_class)
        inheritance_second = InheritanceChecker.get_inheritance(tree, second_class)

        if inheritance_second in inheritance_first or inheritance_first in inheritance_second:
            return True

        return False
