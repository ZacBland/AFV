import numpy as np
from math import sin, cos
from libs.defines import *


class CarDescription:

    def __init__(self, overall_length: float = AFV_OVERALL_LENGTH, overall_width: float = AFV_OVERALL_WIDTH,
                 rear_overhang: float= AFV_REAR_OVERHANG, tire_diameter: float = AFV_TIRE_DIAMETER,
                 tire_width: float = AFV_TIRE_WIDTH, axle_track: float = AFV_AXLE_TRACK,
                 wheelbase: float = AFV_WHEELBASE, max_steer: float = AFV_MAX_STEER):
        """
        Description of a car for visualising vehicle control in Matplotlib.
        All calculations are done w.r.t the vehicle's rear axle to reduce computation steps.

        At initialisation
        :param overall_length:      (float) vehicle's overall length [m]
        :param overall_width:       (float) vehicle's overall width [m]
        :param rear_overhang:       (float) distance between the rear bumper and the rear axle [m]
        :param tire_diameter:       (float) diameter of the vehicle's tire [m]
        :param tire_width:          (float) width of the vehicle's tire [m]
        :param axle_track:          (float) length of the vehicle's axle track [m]
        :param wheelbase:           (float) length of the vehicle's wheelbase [m]

        At every time step
        :param x:                   (float) x-coordinate of the vehicle's rear axle
        :param y:                   (float) y-coordinate of the vehicle's rear axle
        :param yaw:                 (float) vehicle's heading [rad]
        :param steer:               (float) vehicle's steering angle [rad]

        :return outlines:           (ndarray) vehicle's outlines [x, y]
        :return fr_wheel:           (ndarray) vehicle's front-right axle [x, y]
        :return rr_wheel:           (ndarray) vehicle's rear-right axle [x, y]
        :return fl_wheel:           (ndarray) vehicle's front-left axle [x, y]
        :return rl_wheel:           (ndarray) vehicle's rear-right axle [x, y]
        """

        self.overall_length = overall_length
        self.overall_width = overall_width
        self.rear_overhang = rear_overhang
        self.tire_diameter = tire_diameter
        self.tire_width = tire_width
        self.axle_track = axle_track
        self.wheelbase = wheelbase
        self.max_steer = max_steer

        rear_axle_to_front_bumper = overall_length - rear_overhang
        centreline_to_wheel_centre = 0.5 * axle_track
        centreline_to_side = 0.5 * overall_width

        vehicle_vertices = np.array([
            (-rear_overhang, centreline_to_side),
            (rear_axle_to_front_bumper, centreline_to_side),
            (rear_axle_to_front_bumper, -centreline_to_side),
            (-rear_overhang, -centreline_to_side)
        ])

        half_tire_width = 0.5 * tire_width
        centreline_to_inwards_rim = centreline_to_wheel_centre - half_tire_width
        centreline_to_outwards_rim = centreline_to_wheel_centre + half_tire_width

        # Rear right wheel
        wheel_vertices = np.array([
            (-tire_diameter, -centreline_to_inwards_rim),
            (tire_diameter, -centreline_to_inwards_rim),
            (tire_diameter, -centreline_to_outwards_rim),
            (-tire_diameter, -centreline_to_outwards_rim)
        ])

        self.outlines = np.concatenate([vehicle_vertices, [vehicle_vertices[0]]])
        self.wheel_format = np.concatenate([wheel_vertices, [wheel_vertices[0]]])
        self.rl_wheel = self.wheel_format.copy()
        self.rl_wheel[:, 1] *= -1

        fl_wheel = self.rl_wheel.copy()
        fr_wheel = self.wheel_format.copy()
        fl_wheel[:, 0] += wheelbase
        fr_wheel[:, 0] += wheelbase

        # Translate front wheels to origin
        get_face_center = lambda vertices: np.array([
            0.5 * (vertices[0][0] + vertices[2][0]),
            0.5 * (vertices[0][1] + vertices[2][1])
        ])

        self.fr_wheel_centre = get_face_center(fr_wheel)
        self.fl_wheel_centre = get_face_center(fl_wheel)
        self.fr_wheel_origin = fr_wheel - self.fr_wheel_centre
        self.fl_wheel_origin = fl_wheel - self.fl_wheel_centre

        # Class variables
        self.x = None
        self.y = None
        self.yaw_vector = np.empty((2, 2))

    def get_rotation_matrix(self, angle: float) -> np.ndarray:
        return np.array([
            (cos(angle), sin(angle)),
            (-sin(angle), cos(angle))
        ])

    def transform(self, point: np.ndarray) -> np.ndarray:
        # Vector rotation
        point = point.dot(self.yaw_vector).T

        # Vector translation
        point[0, :] += self.x
        point[1, :] += self.y

        return point

    def plot_car(self, x: float, y: float, yaw: float, steer: float) -> tuple[np.ndarray, ...]:
        self.x = x
        self.y = y

        # Rotation matrices
        self.yaw_vector = self.get_rotation_matrix(yaw)
        steer_vector = self.get_rotation_matrix(steer)

        # Rotate the wheels about its position
        fr_wheel = self.fr_wheel_origin.copy()
        fl_wheel = self.fl_wheel_origin.copy()
        fr_wheel = fr_wheel @ steer_vector
        fl_wheel = fl_wheel @ steer_vector
        fr_wheel += self.fr_wheel_centre
        fl_wheel += self.fl_wheel_centre

        outlines = self.transform(self.outlines)
        rr_wheel = self.transform(self.wheel_format)
        rl_wheel = self.transform(self.rl_wheel)
        fr_wheel = self.transform(fr_wheel)
        fl_wheel = self.transform(fl_wheel)

        return outlines, fr_wheel, rr_wheel, fl_wheel, rl_wheel
