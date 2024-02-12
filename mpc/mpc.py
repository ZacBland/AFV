from __future__ import annotations
import numpy as np
from libs.defines import *
from libs import CarDescription, normalize_angle, interpolate_cubic_spline
import math
import cvxpy
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

show_animation = False



class State:
    """
        vehicle state class
        """

    def __init__(self, x=0.0, y=0.0, yaw=0.0, v=0.0):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.v = v
        self.predelta = None


class MPC:

    def __init__(self, car_desc: CarDescription):

        self.NX = 4  # x = x, y, v, yaw
        self.NU = 2  # a = [accel, steer]
        self.T = 5  # Horizon length

        # mpc parameters
        self.R = np.diag([0.01, 0.01])  # input cost matrix
        self.Rd = np.diag([0.01, 1.0])  # input difference cost matrix
        self.Q = np.diag([1.0, 1.0, 0.5, 0.5])  # state cost matrix
        self.Qf = self.Q  # state final matrix
        self.GOAL_DIS = 1.5  # goal distance
        self.STOP_SPEED = 2.0  # stop speed
        self.MAX_TIME = 500.0  # max simulation time

        self.MAX_ITER = 5
        self.DU_TH = 0.1

        self.TARGET_SPEED = mph2ms(20)  # [m/s]
        self.N_IND_SEARCH = 20  # Search Index Number

        self.dt = 0.1

        self.car = car_desc
        self.MAX_STEER = car_desc.max_steer  # maximum steering angle [rad]
        self.MAX_STEER_SPEED = np.deg2rad(30.0)  # maximum steering speed [rad/s]
        self.MAX_SPEED = mph2ms(45.0)  # [m/s]
        self.MIN_SPEED = mph2ms(-10.0)  # [m/s]
        self.MAX_ACCEL = mph2ms(10.0)  # [m/s^2]

    def linear_model_matrix(self, v, phi, delta):

        A = np.zeros((self.NX, self.NX))
        A[0, 0] = 1.0
        A[1, 1] = 1.0
        A[2, 2] = 1.0
        A[3, 3] = 1.0
        A[0, 2] = self.dt * math.cos(phi)
        A[0, 3] = - self.dt * v * math.sin(phi)
        A[1, 2] = self.dt * math.sin(phi)
        A[1, 3] = self.dt * v * math.cos(phi)
        A[3, 2] = self.dt * math.tan(delta) / self.car.wheelbase

        B = np.zeros((self.NX, self.NU))
        B[2, 0] = self.dt
        B[3, 1] = self.dt * v / (self.car.wheelbase * math.cos(delta) ** 2)

        C = np.zeros(self.NX)
        C[0] = self.dt * v * math.sin(phi) * phi
        C[1] = - self.dt * v * math.cos(phi) * phi
        C[3] = - self.dt * v * delta / (self.car.wheelbase * math.cos(delta) ** 2)

        return A, B, C

    def update_state(self, state, a, delta):
        if delta >= self.MAX_STEER:
            delta = self.MAX_STEER
        elif delta <= -self.MAX_STEER:
            delta = -self.MAX_STEER

        state.x = state.x + state.v * math.cos(state.yaw) * self.dt
        state.y = state.y + state.v * math.sin(state.yaw) * self.dt
        state.yaw = state.yaw + state.v / self.car.wheelbase * math.tan(delta) * self.dt
        state.v = state.v + a * self.dt

        if state.v > self.MAX_SPEED:
            state.v = self.MAX_SPEED
        elif state.v < self.MIN_SPEED:
            state.v = self.MIN_SPEED

        return state

    def calc_nearest_index(self, state, cx, cy, cyaw, pind):

        dx = [state.x - icx for icx in cx[pind:(pind + self.N_IND_SEARCH)]]
        dy = [state.y - icy for icy in cy[pind:(pind + self.N_IND_SEARCH)]]

        d = [idx ** 2 + idy ** 2 for (idx, idy) in zip(dx, dy)]

        mind = min(d)

        ind = d.index(mind) + pind

        mind = math.sqrt(mind)

        dxl = cx[ind] - state.x
        dyl = cy[ind] - state.y

        angle = normalize_angle(cyaw[ind] - math.atan2(dyl, dxl))
        if angle < 0:
            mind *= -1

        return ind, mind

    def predict_motion(self, x0, oa, od, xref):
        xbar = xref * 0.0
        for i, _ in enumerate(x0):
            xbar[i, 0] = x0[i]

        state = State(x=x0[0], y=x0[1], yaw=x0[3], v=x0[2])
        for (ai, di, i) in zip(oa, od, range(1, self.T + 1)):
            state = self.update_state(state, ai, di)
            xbar[0, i] = state.x
            xbar[1, i] = state.y
            xbar[2, i] = state.v
            xbar[3, i] = state.yaw

        return xbar

    def iterative_linear_mpc_control(self, xref, x0, dref, oa, od):
        """
        MPC control with updating operational point iteratively
        """
        ox, oy, oyaw, ov = None, None, None, None

        if oa is None or od is None:
            oa = [0.0] * self.T
            od = [0.0] * self.T

        for i in range(self.MAX_ITER):
            xbar = self.predict_motion(x0, oa, od, xref)
            poa, pod = oa[:], od[:]
            oa, od, ox, oy, oyaw, ov = self.linear_mpc_control(xref, xbar, x0, dref)
            du = sum(abs(oa - poa)) + sum(abs(od - pod))  # calc u change value
            if du <= self.DU_TH:
                break
        else:
            print("Iterative is max iter")

        return oa, od, ox, oy, oyaw, ov

    def linear_mpc_control(self, xref, xbar, x0, dref):
        """
        linear mpc control

        xref: reference point
        xbar: operational point
        x0: initial state
        dref: reference steer angle
        """

        x = cvxpy.Variable((self.NX, self.T + 1))
        u = cvxpy.Variable((self.NU, self.T))

        cost = 0.0
        constraints = []

        for t in range(self.T):
            cost += cvxpy.quad_form(u[:, t], self.R)

            if t != 0:
                cost += cvxpy.quad_form(xref[:, t] - x[:, t], self.Q)

            A, B, C = self.linear_model_matrix(
                xbar[2, t], xbar[3, t], dref[0, t])
            constraints += [x[:, t + 1] == A @ x[:, t] + B @ u[:, t] + C]

            if t < (self.T - 1):
                cost += cvxpy.quad_form(u[:, t + 1] - u[:, t], self.Rd)
                constraints += [cvxpy.abs(u[1, t + 1] - u[1, t]) <=
                                self.MAX_STEER_SPEED * self.dt]

        cost += cvxpy.quad_form(xref[:, self.T] - x[:, self.T], self.Qf)

        constraints += [x[:, 0] == x0]
        constraints += [x[2, :] <= self.MAX_SPEED]
        constraints += [x[2, :] >= self.MIN_SPEED]
        constraints += [cvxpy.abs(u[0, :]) <= self.MAX_ACCEL]
        constraints += [cvxpy.abs(u[1, :]) <= self.MAX_STEER]

        prob = cvxpy.Problem(cvxpy.Minimize(cost), constraints)
        prob.solve(solver=cvxpy.ECOS, verbose=False)

        if prob.status == cvxpy.OPTIMAL or prob.status == cvxpy.OPTIMAL_INACCURATE:
            ox = get_nparray_from_matrix(x.value[0, :])
            oy = get_nparray_from_matrix(x.value[1, :])
            ov = get_nparray_from_matrix(x.value[2, :])
            oyaw = get_nparray_from_matrix(x.value[3, :])
            oa = get_nparray_from_matrix(u.value[0, :])
            odelta = get_nparray_from_matrix(u.value[1, :])

        else:
            print("Error: Cannot solve mpc..")
            oa, odelta, ox, oy, oyaw, ov = None, None, None, None, None, None

        return oa, odelta, ox, oy, oyaw, ov

    def calc_ref_trajectory(self, state, cx, cy, cyaw, sp, dl, pind):
        xref = np.zeros((self.NX, self.T + 1))
        dref = np.zeros((1, self.T + 1))
        ncourse = len(cx)

        ind, _ = self.calc_nearest_index(state, cx, cy, cyaw, pind)

        if pind >= ind:
            ind = pind

        xref[0, 0] = cx[ind]
        xref[1, 0] = cy[ind]
        xref[2, 0] = sp[ind]
        xref[3, 0] = cyaw[ind]
        dref[0, 0] = 0.0  # steer operational point should be 0

        travel = 0.0

        for i in range(self.T + 1):
            travel += abs(state.v) * self.dt
            dind = int(round(travel / dl))

            if (ind + dind) < ncourse:
                xref[0, i] = cx[ind + dind]
                xref[1, i] = cy[ind + dind]
                xref[2, i] = sp[ind + dind]
                xref[3, i] = cyaw[ind + dind]
                dref[0, i] = 0.0
            else:
                xref[0, i] = cx[ncourse - 1]
                xref[1, i] = cy[ncourse - 1]
                xref[2, i] = sp[ncourse - 1]
                xref[3, i] = cyaw[ncourse - 1]
                dref[0, i] = 0.0

        return xref, ind, dref

    def check_goal(self, state, goal, tind, nind):

        # check goal
        dx = state.x - goal[0]
        dy = state.y - goal[1]
        d = math.hypot(dx, dy)

        isgoal = (d <= self.GOAL_DIS)

        if abs(tind - nind) >= 5:
            isgoal = False

        isstop = (abs(state.v) <= self.STOP_SPEED)

        if isgoal and isstop:
            return True

        return False

    def calc_speed_profile(self, cx, cy, cyaw, target_speed):

        speed_profile = [target_speed] * len(cx)
        direction = 1.0  # forward

        # Set stop point
        for i in range(len(cx) - 1):
            dx = cx[i + 1] - cx[i]
            dy = cy[i + 1] - cy[i]

            move_direction = math.atan2(dy, dx)

            if dx != 0.0 and dy != 0.0:
                dangle = abs(normalize_angle(move_direction - cyaw[i]))
                if dangle >= math.pi / 4.0:
                    direction = -1.0
                else:
                    direction = 1.0

            if direction != 1.0:
                speed_profile[i] = - target_speed
            else:
                speed_profile[i] = target_speed

        speed_profile[-1] = 0.0

        return speed_profile

    def do_simulation(self, cx, cy, cyaw, sp, dl, initial_state):
        """
        Simulation

        cx: course x position list
        cy: course y position list
        cy: course yaw position list
        sp: speed profile
        dl: course tick [m]

        """

        goal = [cx[-1], cy[-1]]

        state = initial_state

        # initial yaw compensation
        if state.yaw - cyaw[0] >= math.pi:
            state.yaw -= math.pi * 2.0
        elif state.yaw - cyaw[0] <= -math.pi:
            state.yaw += math.pi * 2.0

        time = 0.0
        x = [state.x]
        y = [state.y]
        yaw = [state.yaw]
        v = [state.v]
        t = [0.0]
        d = [0.0]
        a = [0.0]
        target_ind, _ = self.calc_nearest_index(state, cx, cy, cyaw, 0)

        odelta, oa = None, None

        cyaw = smooth_yaw(cyaw)


        while self.MAX_TIME >= time:
            xref, target_ind, dref = self.calc_ref_trajectory(
                state, cx, cy, cyaw, sp, dl, target_ind)

            x0 = [state.x, state.y, state.v, state.yaw]  # current state

            oa, odelta, ox, oy, oyaw, ov = self.iterative_linear_mpc_control(
                xref, x0, dref, oa, odelta)

            di, ai = 0.0, 0.0
            if odelta is not None:
                di, ai = odelta[0], oa[0]
                state = self.update_state(state, ai, di)

            time = time + self.dt

            x.append(state.x)
            y.append(state.y)
            yaw.append(state.yaw)
            v.append(state.v)
            t.append(time)
            d.append(di)
            a.append(ai)

            if self.check_goal(state, goal, target_ind, len(cx)):
                print("Goal")
                break

            if show_animation:  # pragma: no cover

                # for stopping simulation with the esc key.
                plt.gcf().canvas.mpl_connect('key_release_event',
                                             lambda event: [exit(0) if event.key == 'escape' else None])
                if ox is not None:
                    plt.plot(ox, oy, "xr", label="MPC")
                plt.plot(cx, cy, "-r", label="course")
                plt.plot(x, y, "ob", label="trajectory")
                plt.plot(xref[0, :], xref[1, :], "xk", label="xref")
                plt.plot(cx[target_ind], cy[target_ind], "xg", label="target")
                #outlines, fr_wheel, rr_wheel, fl_wheel, rl_wheel = self.car.plot_car(state.x, state.y, state.yaw, di)
                
                #plt.plot(outlines[0], outlines[1], color='black')
                
                #plt.plot(*fr_wheel, color='black')
                #plt.plot(*rr_wheel, color='black')
                #plt.plot(*fl_wheel, color='black')
                #plt.plot(*rl_wheel, color='black')
                
                plt.axis("equal")
                plt.grid(True)
                plt.title("Time[s]:" + str(round(time, 2))
                          + ", speed[mph]:" + str(round(ms2mph(state.v), 2)))
                plt.pause(0.0001)


        return t, x, y, yaw, v, d, a



if __name__ == "__main__":

    mpc = MPC()

    import csv
    with open('../data/test.csv', newline='') as f:
        rows = list(csv.reader(f, delimiter=','))

    ds = 0.05
    px, py = [[float(i) for i in row] for row in zip(*rows[1:])]

    cx, cy, cyaw, _ = interpolate_cubic_spline(px, py, step=ds)

    sp = mpc.calc_speed_profile(cx, cy, cyaw, mpc.TARGET_SPEED)

    initial_state = State(x=cx[0], y=cy[0], yaw=cyaw[0], v=0.0)

    t, x, y, yaw, v, d, a = mpc.do_simulation(cx, cy, cyaw, sp, ds, initial_state)







