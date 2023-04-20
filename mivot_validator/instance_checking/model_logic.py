"""
Created on 20 Apr 2023

@author: julien abid
"""


def model_detector(name):
    """
    Detect the model name from the VODML file name
    :name: VODML file name
    :return: dictionary with the classes and the corresponding error classes
    """
    if name == "meas":
        return {"Position": ["Asymmetrical2D", "Symmetrical", "Bounds2D", "Ellipse"],
                "Velocity": ["Asymmetrical2D", "Symmetrical", "Bounds2D", "Ellipse"],
                "Time": ["Asymmetrical1D", "Symmetrical", "Bounds1D"],
                "Polarization": ["Asymmetrical1D", "Symmetrical", "Bounds1D"],
                "ProperMotion": ["Asymmetrical2D", "Symmetrical", "Ellipse"],
                "GenericMeasure": ["Uncertainty"],
                "Error": ["Uncertainty"],
                }
    else:
        return None
