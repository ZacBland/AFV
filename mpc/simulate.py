from mpc import MPC, State
from libs.cubic_interpolation import interpolate_cubic_spline
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import math
from libs.defines import *
from libs.car_description import CarDescription
import logging

MAX_TIME = 30.0

"""
class Fargs:

    def __init__(self, cx:list, cy:list, ox:list, oy:list, xref, t: list, x: list, y: list, yaw: list, v: list, d: list, a: list, target_ind_list: list):
        self.cx = cx
        self.cy = cy
        self.ox = ox
        self.oy= oy
        self.xref = xref
        self.t = t
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v
        self.d = d
        self.a = a
        self.target_ind_list = target_ind_list
"""

class Simulation:

    def __init__(self, mpc: MPC):

        self.fps = 30.0
        self.map_size_x = 100
        self.map_size_y = 100
        self.frames = None
        self.loop = False
        self.mpc = mpc


    def animate(self, frame, data:dict):
        cx = data['cx']
        cy = data['cy']
        t = data['t']
        xref = data['xref']
        target_ind_list = data['target_ind_list']
        ox = data['ox']
        oy = data['oy']
        yaw = data["yaw"]
        x = data["x"]
        y = data["y"]
        d = data["d"]

        self.ax[0].set_title(f'{t[frame]:.2f}s', loc='right')

        self.mpc_graph.set_data(ox[frame], oy[frame])
        self.xref_graph.set_data(xref[frame][0], xref[frame][1])
        self.xy.set_data(cx[target_ind_list[frame]], cy[target_ind_list[frame]])
        self.trajectory.set_data(x[:frame], y[:frame])

        outline_plot, fr_plot, rr_plot, fl_plot, rl_plot = self.mpc.car.plot_car(x[frame], y[frame], yaw[frame], d[frame])
        self.outline.set_data(outline_plot[0], outline_plot[1])
        self.fr.set_data(*fr_plot)
        self.rr.set_data(*rr_plot)
        self.fl.set_data(*fl_plot)
        self.rl.set_data(*rl_plot)
        self.rear_axle.set_data(x[frame], y[frame])

        self.yaw_arr.append(math.degrees(yaw[frame]))
        self.yaw_data.set_data(np.arange(frame + 1), self.yaw_arr)
        self.ax[1].set_ylim(self.yaw_arr[-1] - 180, self.yaw_arr[-1] + 180)

        self.velocity_arr.append(ms2mph(v[frame]))
        self.velocity_data.set_data(np.arange(frame + 1),  self.velocity_arr)
        self.ax[3].set_ylim(self.velocity_arr[-1] - 20, self.velocity_arr[-1] + 20)


    def create_animation(self, data: dict):
        fig = plt.figure(constrained_layout=True)

        self.ax = fig.subplot_mosaic([[0, 1], [0, 2], [0, 3]], gridspec_kw={'width_ratios': [1, 1]})

        cx = data['cx']
        cy = data['cy']

        self.ax[0].set_aspect('equal')
        self.ax[0].plot(cx, cy, '--', color='red')

        self.frames = len(data['t']) - 1

        self.mpc_graph, = self.ax[0].plot([], [], "xr", label="MPC")
        self.xy, = self.ax[0].plot([], [], "xg", label="target")
        self.trajectory, = self.ax[0].plot([], [], linestyle="-", color="b", label="trajectory")
        self.xref_graph, = self.ax[0].plot([], [], "xk", label="xref")

        self.outline, =  self.ax[0].plot([], [], color='black')
        self.fr, = self.ax[0].plot([], [], color='black')
        self.rr, = self.ax[0].plot([], [], color='black')
        self.fl, = self.ax[0].plot([], [], color='black')
        self.rl, = self.ax[0].plot([], [], color='black')
        self.rear_axle, = self.ax[0].plot(x[0], y[0], '+', color='black', markersize=2)

        self.yaw_arr = []
        self.yaw_data, = self.ax[1].plot([], [])
        self.ax[1].set_xlim(0, self.frames)
        self.ax[1].set_ylabel("Yaw")
        self.ax[1].grid()

        self.velocity_arr = []
        self.velocity_data, =  self.ax[3].plot([], [])
        self.ax[3].set_xlim(0, self.frames)
        self.ax[3].set_ylabel("Velocity")
        self.ax[3].grid()

        anim = FuncAnimation(fig, self.animate, frames=self.frames, init_func=lambda: None, fargs=[data],
                             interval=(1.0/self.fps)*1000, repeat=self.loop)
        fig.set_size_inches(18.5, 10.5, forward=True)
        plt.show()


    def simulate(self, cx, cy, cyaw, sp, dt, initial_state):
        self.goal = [cx[-1], cy[-1]]

        state = initial_state

        # initial yaw compensation
        if state.yaw - cyaw[0] >= math.pi:
            state.yaw -= math.pi * 2.0
        elif state.yaw - cyaw[0] <= -math.pi:
            state.yaw += math.pi * 2.0

        time = 0.0
        x = [state.x]
        y = [state.y]
        oxs = []
        oys = []
        yaw = [state.yaw]
        v = [state.v]
        t = [0.0]
        d = [0.0]
        a = [0.0]
        target_ind_list = []
        x_ref_list = []
        target_ind, _ = self.mpc.calc_nearest_index(state, cx, cy, cyaw, 0)

        odelta, oa = None, None

        cyaw = smooth_yaw(cyaw)

        logging.basicConfig(filename='sim.log', level=logging.INFO)

        while MAX_TIME >= time:
            xref, target_ind, dref = self.mpc.calc_ref_trajectory(state, cx, cy, cyaw, sp, dt, target_ind)

            x0 = [state.x, state.y, state.v, state.yaw]  # current state

            oa, odelta, ox, oy, oyaw, ov = self.mpc.iterative_linear_mpc_control(xref, x0, dref, oa, odelta)

            di, ai = 0.0, 0.0
            if odelta is not None:
                di, ai = odelta[0], oa[0]
                state = self.mpc.update_state(state, ai, di)

            time = time + dt

            x.append(state.x)
            y.append(state.y)
            x_ref_list.append(xref)
            oxs.append(ox)
            oys.append(oy)
            yaw.append(state.yaw)
            v.append(state.v)
            t.append(time)
            d.append(di)
            a.append(ai)
            target_ind_list.append(target_ind)

            if self.mpc.check_goal(state, self.goal, target_ind, len(cx)):
                print("Goal")
                break

        return t, x, y, oxs, oys, x_ref_list, yaw, v, d, a, target_ind_list


if __name__ == "__main__":
    car_desc = CarDescription()
    mpc = MPC(car_desc)

    with open('../data/test.csv', newline='') as f:
        rows = list(csv.reader(f, delimiter=','))
    px, py = [[float(i) for i in row] for row in zip(*rows[1:])]

    dt = 0.05
    cx, cy, cyaw, _ = interpolate_cubic_spline(px, py, step=dt)
    sp = mpc.calc_speed_profile(cx, cy, cyaw, mpc.TARGET_SPEED)
    initial_state = State(x=cx[0], y=cy[0], yaw=cyaw[0], v=0.0)

    sim = Simulation(mpc)
    t, x, y, ox, oy, xref, yaw, v, d, a, target_ind_list = sim.simulate(cx, cy, cyaw, sp, dt, initial_state)

    data = {
        "cx": cx,
        "cy": cy,
        "t": t,
        "x": x,
        "y": y,
        "ox": ox,
        "oy": oy,
        "xref": xref,
        "yaw": yaw,
        "v": v,
        "d": d,
        "a": a,
        "target_ind_list": target_ind_list
    }

    sim.create_animation(data)
