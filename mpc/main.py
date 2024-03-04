from mpc.mpc import MPC
from radio import Packet
from libs import CarDescription


class NavControl:

    def __init__(self, car_desc: CarDescription, max_speed=20.0):
        """
        Live controller for Autonomous Firefighting Vehicle using MPC to control
        steering and velocity throughout the course of the vehicle.
        """


