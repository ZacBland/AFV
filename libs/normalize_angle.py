from math import cos, sin, atan2

def normalize_angle(angle: float):
    return atan2(sin(angle), cos(angle))