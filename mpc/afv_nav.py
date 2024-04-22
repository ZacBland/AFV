from mpc import MPC, State
from GPS import Wit
from libs import CarDescription, latlon2xyz, xyz2latlon, mph2ms, ms2mph, interpolate_cubic_spline, smooth_yaw
from search import Graph
from search.a_star import a_star_search, reconstruct_path
from shapely.geometry import LineString
import math
import numpy as np
import json


class NavControl:

    def __init__(self, car_desc: CarDescription, goal=None):
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

        self.gps = Wit()

        with open('../logs/airport_test.json') as file:
            data = json.load(file)

        graph = Graph.from_dict(data)

        if goal is None:
            self.goal = graph.get_node_from_name("51")
        else:
            self.goal = goal

        came_from, cost_so_far = a_star_search(graph, graph.nodes[0], self.goal)
        path = reconstruct_path(came_from, graph.nodes[0], self.goal)

        n = 100
        line = LineString(list(map(lambda x: x.pos, path)))
        distances = np.linspace(0, line.length, n)
        points = [line.interpolate(distance) for distance in distances]
        xyz = [latlon2xyz(point.x, point.y) for point in points]

        px = [x[0] for x in xyz]
        py = [y[1] for y in xyz]

        self.cx, self.cy, self.cyaw, self.ccur = interpolate_cubic_spline(px, py, step=0.01)
        self.sp = self.mpc.calc_speed_profile(self.cx, self.cy, self.cyaw, self.ccur, self.mpc.TARGET_SPEED)

        from matplotlib import pyplot as plt
        plt.plot(self.cx, self.cy)
        plt.show()

        # initalize state
        # todo: Read values from IMU/GPS
        self.state = State(x=self.cx[0], y=self.cy[0], yaw=90, v=0.0)

        if self.state.yaw - self.cyaw[0] >= math.pi:
            self.state.yaw -= math.pi * 2.0
        elif self.state.yaw - self.cyaw[0] <= -math.pi:
            self.state.yaw += math.pi * 2.0

        x,y,_ = latlon2xyz(self.goal.pos[0], self.goal.pos[1])
        self.goal = [x,y]

        self.time = 0.0
        self.x = [self.state.x]
        self.y = [self.state.y]
        self.oxs = []
        self.oys = []
        self.yaw = [self.state.yaw]
        self.v = [self.state.v]
        self.t = [0.0]
        self.d = [0.0]
        self.a = [0.0]
        self.target_ind_list = []
        self.x_ref_list = []
        self.target_ind, _ = self.mpc.calc_nearest_index(self.state, self.cx, self.cy, self.cyaw, 0)

        self.cyaw = smooth_yaw(self.cyaw)

    def read_current_state(self):
        lat = self.gps.data["lat"]
        lon = self.gps.data["lon"]
        yaw = self.gps.data["Yaw"]
        velo = self.gps.data["Speed"]

        if lat == 0.0 or lon == 0.0:
            print("GPS not locked on.")

    def accel_to_speed(self, a):
        pass

    def run(self):
        odelta, oa = None, None
        #while #not self.mpc.check_goal(self.state, self.goal, self.target_ind, len(self.cx)):
        while True:

            xref, self.target_ind, dref = self.mpc.calc_ref_trajectory(self.state, self.cx, self.cy, self.cyaw, self.sp, self.mpc.dt, self.target_ind)
            x0 = [self.state.x, self.state.y, self.state.v, self.state.yaw]  # current state

            oa, odelta, ox, oy, oyaw, ov = self.mpc.iterative_linear_mpc_control(xref, x0, dref, oa, odelta)

            print(oa[0]*self.mpc.dt)
            print(odelta[0])

            self.read_current_state()




if __name__ == "__main__":
    car_desc = CarDescription()
    nav = NavControl(car_desc)
    nav.run()
