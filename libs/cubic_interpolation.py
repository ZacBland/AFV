
from numpy.typing import ArrayLike, NDArray
import numpy as np
from scipy.interpolate import CubicSpline


def interpolate_cubic_spline(x: ArrayLike, y: ArrayLike, step: float=0.05, condition: str='natural') -> tuple[NDArray, ...]:
    """
    Function to generate cubic spline for path
    :param x: ArrayLike points of x
    :param y: ArrayLike points of y
    :param step: Step size for derivation
    :param condition: Cubic Spline Condition
    :return:
    """
    distances = np.concatenate((np.zeros(1), np.cumsum(np.hypot(np.ediff1d(x), np.ediff1d(y)))))
    points = np.array([x, y]).T
    s = np.arange(0, distances[-1], step)
    cubic_spline = CubicSpline(distances, points, bc_type=condition, axis=0, extrapolate=False)

    dx, dy = cubic_spline.derivative(1)(s).T
    yaw = np.arctan2(dy, dx)

    ddx, ddy = cubic_spline.derivative(2)(s).T
    curvature = (ddy * dx - ddx * dy) / ((dx * dx + dy * dy) ** 1.5)

    spline_x, spline_y = cubic_spline(s).T

    return spline_x, spline_y, yaw, curvature
