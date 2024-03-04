from mpc import MPC, State
from libs.cubic_interpolation import interpolate_cubic_spline
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import math
from libs.defines import *
from libs.car_description import CarDescription
import logging
import codecs, json
from libs import normalize_angle


class Simulation:

    def __init__(self, mpc: MPC):

        self.fps = 60
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
        x = data["x"]
        y = data["y"]
        yaw = data['yaw']
        d = data['d']

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

        # Draw Car Plot
        desc_plots = self.mpc.car.plot_car(0, 0, yaw[frame], d[frame])
        outlines = desc_plots[0]
        center = ((outlines[0][0]+outlines[0][2])/2,(outlines[1][0]+outlines[1][2])/2)
        self.car_ax.clear()
        from matplotlib.patches import Rectangle
        self.car_ax.add_patch(Rectangle((center[0]-1, center[1]-1), 2, 2, fill=False, lw=0))
        for desc_plot in desc_plots:
            self.car_ax.plot(*desc_plot, color="black")
        self.car_ax.set_yticks([])
        self.car_ax.set_xticks([])
        self.car_ax.invert_yaxis()

        self.mpc_ax.set_xlim(x[frame] - 200, x[frame] + 200)
        self.mpc_ax.set_ylim(y[frame] + 200, y[frame] - 200)

        #Draw Yaw Graph
        self.yaw_arr.append(math.degrees(normalize_angle(yaw[frame])))
        self.yaw_data.set_data(np.arange(frame + 1), self.yaw_arr)
        self.yaw_follower_y.set_data([0, frame], [self.yaw_arr[frame], self.yaw_arr[frame]])
        self.yaw_follower_x.set_data([frame, frame], [0, self.yaw_arr[frame]])
        self.yaw_follower_text.set_x(frame)
        self.yaw_follower_text.set_y(self.yaw_arr[frame])
        self.yaw_follower_text.set_text(str(round(self.yaw_arr[frame])))
        self.yaw_ax.set_ylim(-180, 180)

        # Draw Steering Angle Graph
        self.d_arr.append(math.degrees(normalize_angle(d[frame])))
        self.d_data.set_data(np.arange(frame + 1), self.d_arr)
        self.d_follower_y.set_data([0, frame], [self.d_arr[frame], self.d_arr[frame]])
        self.d_follower_x.set_data([frame, frame], [0, self.d_arr[frame]])
        self.d_follower_text.set_x(frame)
        self.d_follower_text.set_y(self.d_arr[frame])
        self.d_follower_text.set_text(str(round(self.d_arr[frame],3)))
        self.d_ax.set_ylim(-math.degrees(self.mpc.MAX_STEER)-10, math.degrees(self.mpc.MAX_STEER)+10)

        #Draw Velo Graph
        v = data['v']
        self.velocity_arr.append(ms2mph(v[frame]))
        self.velocity_data.set_data(np.arange(frame + 1),  self.velocity_arr)
        self.velocity_follower_y.set_data([0, frame], [self.velocity_arr[frame], self.velocity_arr[frame]])
        self.velocity_follower_x.set_data([frame, frame], [0, self.velocity_arr[frame]])
        self.velocity_follower_text.set_x(frame)
        self.velocity_follower_text.set_y(self.velocity_arr[frame])
        self.velocity_follower_text.set_text(str(round(self.velocity_arr[frame])))
        self.v_ax.set_ylim(-15, 50)

        #Draw Error Graph
        self.error_arr.append(abs(math.dist((x[frame], y[frame]),
                                            (cx[target_ind_list[frame]], cy[target_ind_list[frame]]))))
        self.error_data.set_data(np.arange(frame + 1), self.error_arr)
        self.err_ax.set_ylim(0, max(self.error_arr) + 1)
        self.err_text.set_text(f"Avg Err: {round(np.average(self.error_arr),3)}")


    def create_animation(self, data: dict, img_str = None, img_scale = None):
        fig = plt.figure(constrained_layout=True)

        self.ax = fig.subplot_mosaic([[0, 1], [0, 2], [0, 3], [0, 4], [0, 5]], gridspec_kw={'width_ratios': [2, 1]})
        self.mpc_ax = self.ax[0]
        self.car_ax = self.ax[1]
        self.yaw_ax = self.ax[2]
        self.d_ax = self.ax[3]
        self.v_ax = self.ax[4]
        self.err_ax = self.ax[5]
        self.mpc_ax.set_aspect('equal')
        self.car_ax.set_aspect('equal')

        cx = data['cx']
        cy = data['cy']
        x = data['x']
        y = data['y']

        img = None
        if img_str is not None:
            from PIL import Image
            img = Image.open(img_str)

            if img_scale is not None:
                width, height = img.size
                img = img.resize((int(width*img_scale[0]), int(height*img_scale[1])))

            self.mpc_ax.imshow(img, origin="lower")



        if "sp" in data:
            sp = data['sp']

            from shapely.geometry import LineString
            from shapely.ops import unary_union

            n = len(sp)
            line = LineString(zip(cx, cy))

            distances = np.linspace(0, line.length, n)
            points = [line.interpolate(distance) for distance in distances]

            xs = [point.x for point in points]
            ys = [point.y for point in points]

            points = np.array([xs,ys]).T.reshape(-1,1,2)

            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            from matplotlib.collections import LineCollection

            lc = LineCollection(segments=segments, cmap=plt.get_cmap('inferno_r'), norm=plt.Normalize(0, max(sp)))
            lc.set_array(sp)
            self.ax[0].add_collection(lc)

        self.frames = len(data['t']) - 1

        self.mpc_graph, = self.mpc_ax.plot([], [], "xr", label="MPC")
        self.xy, = self.mpc_ax.plot([], [], "xg", label="target")
        self.trajectory, = self.mpc_ax.plot([], [], linestyle="-", color="b", label="trajectory")
        self.xref_graph, = self.mpc_ax.plot([], [], "xk", label="xref")

        self.outline, =  self.mpc_ax.plot([], [], color='black')
        self.fr, = self.mpc_ax.plot([], [], color='black')
        self.rr, = self.mpc_ax.plot([], [], color='black')
        self.fl, = self.mpc_ax.plot([], [], color='black')
        self.rl, = self.mpc_ax.plot([], [], color='black')
        self.rear_axle, = self.mpc_ax.plot(x[0], y[0], '+', color='black', markersize=2)

        self.yaw_arr = []
        self.yaw_data, = self.yaw_ax.plot([], [])
        self.yaw_follower_y, = self.yaw_ax.plot([], [], linestyle="--", color="orange")
        self.yaw_follower_x, = self.yaw_ax.plot([], [], linestyle="-", color="orange")
        self.yaw_follower_text = self.yaw_ax.text(0, 0, "")
        self.yaw_ax.set_xlim(0, self.frames)
        self.yaw_ax.set_title("Yaw (Deg)")
        self.yaw_ax.grid()

        self.d_arr = []
        self.d_data, = self.d_ax.plot([], [])
        self.d_follower_y, = self.d_ax.plot([], [], linestyle="--", color="orange")
        self.d_follower_x, = self.d_ax.plot([], [], linestyle="-", color="orange")
        self.d_follower_text = self.d_ax.text(0, 0, "")
        self.d_ax.set_xlim(0, self.frames)
        self.d_ax.set_title("Steering Angle (Deg)")
        self.d_ax.grid()

        self.velocity_arr = []
        self.velocity_data, =  self.v_ax.plot([], [])
        self.velocity_follower_y, = self.v_ax.plot([], [], linestyle="--", color="orange")
        self.velocity_follower_x, = self.v_ax.plot([], [], linestyle="-", color="orange")
        self.velocity_follower_text = self.v_ax.text(0, 0, "")
        self.v_ax.set_xlim(0, self.frames)
        self.v_ax.set_title("Velocity (MPH)")
        self.v_ax.grid()

        self.error_arr = []
        self.error_data, = self.err_ax.plot([], [])
        self.err_ax.set_xlim(0, self.frames)
        self.err_ax.set_title("Error (M)")
        self.err_text = self.err_ax.text(0.43, 0.90, "", transform=self.err_ax.transAxes)
        self.err_ax.grid()

        anim = FuncAnimation(fig, self.animate, frames=self.frames, init_func=lambda: None, fargs=[data],
                             interval=(1.0/self.fps)*1000, repeat=self.loop)

        from matplotlib.animation import PillowWriter
        writer = PillowWriter(fps=50, metadata=dict(artist='Me'), bitrate=1800)
        anim.save('MPC.gif', writer=writer)
        fig.set_size_inches(18.5, 10.5, forward=True)
        plt.tight_layout()
        #plt.show()


    def simulate(self, cx, cy, cyaw, sp, dt, initial_state, save_sim = True, name="sim"):
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

        while 100.0 >= time:
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

        sim_data = {
            "cx": cx,
            "cy": cy,
            "t": t,
            "x": x,
            "y": y,
            "sp": sp,
            "ox": oxs,
            "oy": oys,
            "xref": x_ref_list,
            "yaw": yaw,
            "v": v,
            "d": d,
            "a": a,
            "target_ind_list": target_ind_list
        }

        if save_sim:
            save_data = sim_data.copy()
            with open(f"../data/{name}.json", "w") as outfile:
                for key in sim_data:
                    if type(sim_data[key]) is np.ndarray:
                        save_data[key] = sim_data[key].tolist()
                    else:
                        save_data[key] = sim_data[key]
                    for i in range(len(save_data[key])):
                        if type(save_data[key][i]) is np.ndarray:
                            save_data[key][i] = save_data[key][i].tolist()
                json.dump(save_data, outfile)

        return sim_data

    def dict_from_json(self, file):
        data_dict = json.load(open(file, 'r'))
        return data_dict


if __name__ == "__main__":

    car_desc = CarDescription()
    mpc = MPC(car_desc)
    sim = Simulation(mpc)

    name = "a_star_waypoints"
    with open(f'../data/sat_scale.csv', newline='') as f:
        rows = list(csv.reader(f, delimiter=','))
    width = float(rows[0][0])
    height = float(rows[0][1])

    calc_sim = True
    if calc_sim:
        with open(f'../data/{name}.csv', newline='') as f:
            rows = list(csv.reader(f, delimiter=','))
        px, py = [[float(i) for i in row] for row in zip(*rows[1:])]

        cx, cy, cyaw, ccur = interpolate_cubic_spline(px, py, step=sim.mpc.dt)

        sp = mpc.calc_speed_profile(cx, cy, cyaw, ccur, mpc.TARGET_SPEED)
        initial_state = State(x=cx[0], y=cy[0], yaw=cyaw[0], v=0.0)

        sim.simulate(cx, cy, cyaw, sp, sim.mpc.dt, initial_state, name=name)

    data = sim.dict_from_json(f"../data/{name}.json")
    sim.create_animation(data, "../images/sat_img.png", (width, height))


