import unittest
from libs import *
from math import pi

class TestLibMethods(unittest.TestCase):

    def test_normalize_angle(self):

        angle = normalize_angle(3*pi)
        self.assertAlmostEqual(angle, pi)


    def test_car_defines(self):

        from matplotlib import pyplot as plt
        import numpy as np

        colour = 'black'

        # Initial state
        x = 30.0
        y = -10.0
        yaw = np.pi / 4
        steer = np.deg2rad(15)

        desc = CarDescription(AFV_OVERALL_LENGTH, AFV_OVERALL_WIDTH, AFV_REAR_OVERHANG, AFV_TIRE_DIAMETER,
                              AFV_TIRE_WIDTH, AFV_AXLE_TRACK, AFV_WHEELBASE)
        desc_plots = desc.plot_car(x, y, yaw, steer)

        ax = plt.axes()
        ax.set_aspect('equal')

        for desc_plot in desc_plots:
            ax.plot(*desc_plot, color=colour)

        plt.show()