import csv
import numpy as np

from math import radians
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from libs import CarDescription, KinematicModel,interpolate_cubic_spline
from stanley_controller import StanleyController


class Simulation:

    def __init__(self):

        fps = 50.0

        self.dt = 1/fps
        self.map_size_x = 100
        self.map_size_y = 100
        self.frames = 720
        self.loop = False


class Path:

    def __init__(self):

        # Get path to waypoints.csv
        with open('../data/a_star_waypoints.csv', newline='') as f:
            rows = list(csv.reader(f, delimiter=','))

        ds = 0.05
        x, y = [[float(i) for i in row] for row in zip(*rows[1:])]

        self.px, self.py, self.pyaw, _ = interpolate_cubic_spline(x, y, ds, "natural")


class Car:

    def __init__(self, init_x, init_y, init_yaw, sim_params, path_params):
        # Model parameters
        self.x = init_x
        self.y = init_y
        self.yaw = init_yaw
        self.target_velocity = 50.0
        self.delta = 0.0
        self.wheelbase = 2.5
        self.max_steer = radians(33)
        self.dt = sim_params.dt
        self.c_r = 0.01
        self.c_a = 2.0
        self.v = 0.0

        # Tracker parameters
        self.px = path_params.px
        self.py = path_params.py
        self.pyaw = path_params.pyaw
        self.k = 8.0
        self.kp = 1.0
        self.ksoft = 1.0
        self.kyaw = 0.0
        self.ksteer = 0.0
        self.crosstrack_error = None
        self.target_id = None

        # Description parameters
        self.overall_length = 4.97
        self.overall_width = 1.964
        self.tyre_diameter = 0.4826
        self.tyre_width = 0.265
        self.axle_track = 1.7
        self.rear_overhang = (self.overall_length - self.wheelbase) / 2

        self.tracker = StanleyController(self.k, self.kp, self.ksoft, self.kyaw, self.ksteer, self.max_steer, self.wheelbase,
                                         self.px, self.py, self.pyaw)
        self.kbm = KinematicModel(self.wheelbase, self.dt)

    def drive(self):
        acceleration = self.tracker.pid_control(50.0, self.v)
        self.v += acceleration * self.dt
        self.delta, self.target_id, self.crosstrack_error = self.tracker.stanley_control(self.x, self.y, self.yaw,
                                                                                         self.v, self.delta)
        self.x, self.y, self.yaw = self.kbm.kinematic_model(self.x, self.y, self.yaw, self.v, self.delta)


class Fargs:

    def __init__(self, ax, sim, path, car, desc, outline, fr, rr, fl, rl, rear_axle, annotation, target, yaw_arr,
                 yaw_data, crosstrack_arr, crosstrack_data, velocity_arr, velocity_data):
        self.ax = ax
        self.sim = sim
        self.path = path
        self.car = car
        self.desc = desc
        self.outline = outline
        self.fr = fr
        self.rr = rr
        self.fl = fl
        self.rl = rl
        self.rear_axle = rear_axle
        self.annotation = annotation
        self.target = target
        self.yaw_arr = yaw_arr
        self.yaw_data = yaw_data
        self.crosstrack_arr = crosstrack_arr
        self.crosstrack_data = crosstrack_data
        self.velocity_arr = velocity_arr
        self.velocity_data = velocity_data


def animate(frame, fargs):
    ax = fargs.ax
    sim = fargs.sim
    path = fargs.path
    car = fargs.car
    desc = fargs.desc
    outline = fargs.outline
    fr = fargs.fr
    rr = fargs.rr
    fl = fargs.fl
    rl = fargs.rl
    rear_axle = fargs.rear_axle
    annotation = fargs.annotation
    target = fargs.target
    yaw_arr = fargs.yaw_arr
    yaw_data = fargs.yaw_data
    crosstrack_arr = fargs.crosstrack_arr
    crosstrack_data = fargs.crosstrack_data
    velocity_arr = fargs.velocity_arr
    velocity_data = fargs.velocity_data


    ax[0].set_title(f'{sim.dt * frame:.2f}s', loc='right')

    # Camera tracks car
    ax[0].set_xlim(car.x - 100, car.x + 100)
    ax[0].set_ylim(car.y + 100, car.y - 100)

    # Drive and draw car
    car.drive()
    outline_plot, fr_plot, rr_plot, fl_plot, rl_plot = desc.plot_car(car.x, car.y, car.yaw, car.delta)
    outline.set_data(outline_plot[0], outline_plot[1])
    fr.set_data(*fr_plot)
    rr.set_data(*rr_plot)
    fl.set_data(*fl_plot)
    rl.set_data(*rl_plot)
    rear_axle.set_data(car.x, car.y)

    # Show car's target
    target.set_data(path.px[car.target_id], path.py[car.target_id])

    # Annotate car's coordinate above car
    annotation.set_text(f"Crosstrack error: {car.crosstrack_error:.5f}")
    annotation.set_position((car.x - 10, car.y + 5))

    # Animate yaw
    yaw_arr.append(car.yaw)
    yaw_data.set_data(np.arange(frame + 1), yaw_arr)
    ax[1].set_ylim(yaw_arr[-1] - 5, yaw_arr[-1] + 5)

    # Animate crosstrack error
    crosstrack_arr.append(car.crosstrack_error)
    crosstrack_data.set_data(np.arange(frame + 1), crosstrack_arr)
    ax[2].set_ylim(crosstrack_arr[-1] - 1, crosstrack_arr[-1] + 1)

    velocity_arr.append(car.v)
    velocity_data.set_data(np.arange(frame + 1), velocity_arr)
    ax[3].set_ylim(velocity_arr[-1] - 50, velocity_arr[-1] + 50)

    return outline, fr, rr, fl, rl, rear_axle, target, yaw_data, crosstrack_data, velocity_data


def main():
    sim = Simulation()
    path = Path()
    car = Car(path.px[0], path.py[0], path.pyaw[0], sim, path)
    desc = CarDescription(car.overall_length, car.overall_width, car.rear_overhang, car.tyre_diameter, car.tyre_width,
                          car.axle_track, car.wheelbase)

    interval = sim.dt * 10 ** 3

    fig = plt.figure(constrained_layout=True)

    ax = fig.subplot_mosaic([[0, 1], [0, 2], [0, 3]],
                             gridspec_kw={'width_ratios': [1, 1]})

    ax[0].set_aspect('equal')
    ax[0].plot(path.px, path.py, '--', color='red')

    import matplotlib.image as image
    sat = image.imread("../images/sat_img.PNG")
    ax[0].imshow(sat)

    annotation = ax[0].annotate(f"Crosstrack error: {float('inf')}", xy=(car.x - 10, car.y + 5), color='black',
                                annotation_clip=False)
    target, = ax[0].plot([], [], '+r')

    outline, = ax[0].plot([], [], color='black')
    fr, = ax[0].plot([], [], color='black')
    rr, = ax[0].plot([], [], color='black')
    fl, = ax[0].plot([], [], color='black')
    rl, = ax[0].plot([], [], color='black')
    rear_axle, = ax[0].plot(car.x, car.y, '+', color='black', markersize=2)
    #ax[0].figure.set_size_inches(10,10)

    yaw_arr = []
    yaw_data, = ax[1].plot([], [])
    ax[1].set_xlim(0, sim.frames)
    ax[1].set_ylabel("Yaw")
    ax[1].grid()

    crosstrack_arr = []
    crosstrack_data, = ax[2].plot([], [])
    ax[2].set_xlim(0, sim.frames)
    ax[2].set_ylabel("Crosstrack error")
    ax[2].grid()

    velocity_arr = []
    velocity_data, = ax[3].plot([], [])
    ax[3].set_xlim(0, sim.frames)
    ax[3].set_ylabel("Velocity")
    ax[3].grid()

    fig.set_size_inches(15,10,forward=True)
    fig.tight_layout()

    fargs = [
        Fargs(
            ax=ax,
            sim=sim,
            path=path,
            car=car,
            desc=desc,
            outline=outline,
            fr=fr,
            rr=rr,
            fl=fl,
            rl=rl,
            rear_axle=rear_axle,
            annotation=annotation,
            target=target,
            yaw_arr=yaw_arr,
            yaw_data=yaw_data,
            crosstrack_arr=crosstrack_arr,
            crosstrack_data=crosstrack_data,
            velocity_arr=velocity_arr,
            velocity_data=velocity_data
        )
    ]

    from matplotlib.animation import PillowWriter
    anim = FuncAnimation(fig, animate, frames=sim.frames, init_func=lambda: None, fargs=fargs, interval=interval,
                      repeat=sim.loop)
    #writer = PillowWriter(fps=50, metadata=dict(artist='Me'), bitrate=1800)
    #anim.save('stanley.gif', writer=writer)
    #anim.save('animation.gif', writer='imagemagick', fps=50)
    plt.show()

    print(f"Mean yaw: {np.mean(yaw_arr)}")
    print(f"Mean crosstrack error: {np.mean(crosstrack_arr)}")


if __name__ == '__main__':
    main()