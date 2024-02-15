from typing import Tuple
import numpy as np
import math

Location = Tuple[float, float]

# AFV Car Defines (meters)
AFV_OVERALL_LENGTH = 60/39.37
AFV_OVERALL_WIDTH = 24/39.37
AFV_TIRE_DIAMETER = 6.5/39.37
AFV_TIRE_WIDTH = 4.5/39.37
AFV_AXLE_TRACK = 24/39.37
AFV_WHEELBASE = 36/39.37
AFV_REAR_OVERHANG = 0.5 * (AFV_OVERALL_LENGTH - AFV_WHEELBASE)
AFV_MAX_STEER = np.deg2rad(20)


def mph2ms(mph: float):
    """
    Function to convert miles per hour to meters per second
    :param mph: float Miles per Hour
    :return: float Meters per Second
    """
    return mph / 2.237

def ms2mph(ms: float):
    """
    Function to convert meters per second to miles per hour
    :param ms: float meters per second
    :return: float: miles per hour
    """
    return ms * 2.237


def smooth_yaw(yaw):

    for i in range(len(yaw) - 1):
        dyaw = yaw[i + 1] - yaw[i]

        while dyaw >= math.pi / 2.0:
            yaw[i + 1] -= math.pi * 2.0
            dyaw = yaw[i + 1] - yaw[i]

        while dyaw <= -math.pi / 2.0:
            yaw[i + 1] += math.pi * 2.0
            dyaw = yaw[i + 1] - yaw[i]

    return yaw

def get_nparray_from_matrix(x):
    return np.array(x).flatten()