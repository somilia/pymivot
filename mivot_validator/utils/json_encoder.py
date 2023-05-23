"""
Created on 1 avr. 2020

@author: laurentmichel
"""

import json
import numpy


class MyEncoder(json.JSONEncoder):
    """
    classdocs
    """

    def default(self, o):
        if isinstance(o, numpy.integer):
            return int(o)
        if isinstance(o, numpy.floating):
            return float(o)
        if isinstance(o, numpy.ndarray):
            return o.tolist()
        return super().default(o)
