"""
Created on 25 Jan 2022

@author: laurentmichel
"""


class QuantityConverter:
    """
    classdocs
    """

    def __init__(self, params):
        """
        Constructor
        """

    @staticmethod
    def parallax_to_distance(parallax):
        """
        Parallax given in mas
        distance returned in parsec
        """
        # https://edu.obs-mip.fr/la-parallaxe-grace-au-satellite-gaia/
        if parallax == 0:
            return float("Inf")
        if parallax < 0:
            return -1 / (parallax / 1000.0)
        return 1 / (parallax / 1000.0)
