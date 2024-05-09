import math

R = 6371000 # Radius of Earth in meters


def latlon2xyz(latitude, longitude):
    """
    Function to convert latitude and longitude to Cartesian coordinates for easier
    manipulation.
    :param latitude: (Float) Latitude in decimal format of Coordinates
    :param longitude: (Float) Longitude in decimal format of Coordinates
    :return: x y z coordinates
    """
    x = R * math.cos(math.radians(latitude)) * math.cos(math.radians(longitude))
    y = R * math.cos(math.radians(latitude)) * math.sin(math.radians(longitude))
    z = R * math.sin(math.radians(longitude))

    return x, y, z


def xyz2latlon(x,y,z):
    """
    Function to convert Cartesian coordinates back to Latitude and Longitude
    :param x: Float
    :param y: Float
    :param z: Float
    :return: Latitude and Longitude in decimal representation
    """
    lat = math.asin(z/R)
    lon = math.atan2(y,x)

    return lat, lon
