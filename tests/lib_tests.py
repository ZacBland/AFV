import unittest
from libs import *
from math import *
from matplotlib import pyplot as plt
import numpy as np

class TestLibMethods(unittest.TestCase):

    def test_normalize_angle(self):

        angle = normalize_angle(3*pi)
        self.assertAlmostEqual(angle, pi)


    def test_car_defines(self):

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

    def test_interpolation(self):
        name = "sharp"
        import csv
        with open(f'../data/{name}.csv', newline='') as f:
            rows = list(csv.reader(f, delimiter=','))
        px, py = [[float(i) for i in row] for row in zip(*rows[1:])]

        cx, cy, cyaw, ccur = interpolate_cubic_spline(px,py, step=0.01)

        fig, ax = plt.subplots(4, 1)

        ax[0].set_aspect("equal")
        ax[0].plot(cx, cy)

        t = range(0, len(cyaw))
        ax[1].plot(t, cyaw)

        t = range(0, len(ccur))
        ax[2].plot(t, ccur)

        def braking_func(x):
            pass
        t = range(0, len(ccur))
        braking = [math.log(abs(x)+1) for x in ccur]
        ax[3].plot(t, braking)

        plt.show()


