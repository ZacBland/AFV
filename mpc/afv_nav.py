from mpc import MPC, State
from libs import CarDescription, latlon2xyz, xyz2latlon, mph2ms, ms2mph
import math


class NavControl:

    def __init__(self, car_desc: CarDescription):
        """
        Live controller for Autonomous Firefighting Vehicle using MPC to control
        steering and velocity throughout the course of the vehicle.
        :param car_desc: (CarDescription) Description object of the car itself
        :param goal: (Tuple) Goal position of latitude and longitude for end position
        """

        self.car_desc = car_desc

        # Initialize MPC
        self.mpc = MPC(car_desc)
        self.mpc.MAX_SPEED = mph2ms(20)
        self.mpc.MAX_STEER_SPEED = math.radians(5.0)  # maximum steering speed [rad/s]
        self.mpc.MIN_SPEED = mph2ms(-20.0)  # [m/s]
        self.mpc.MAX_ACCEL = mph2ms(15.0)  # [m/s^2]
        self.mpc.TARGET_SPEED = mph2ms(15)

    def initialize(self, goal):
        """
        Initialize Run with goal and simulation parameters
        :param goal: (Tuple) Goal position of latitude and longitude for end position
        :return: (Boolean) Return true if initialize is successful
        """

        # Get current position of AFV

        # Initialize Graph


        # A* search to goal position
        x, y, z = latlon2xyz(36.15455128778722, -97.0815499489699)



        # Create cubic spline of drive

if __name__ == "__main__":
    car_desc = CarDescription()
    nav = NavControl(car_desc)
    nav.initialize((0, 0))
