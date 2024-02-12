import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.animation as ani
import matplotlib
from matplotlib.animation import PillowWriter
from search.graph import *
from search.a_star.a_star import *
import random

graph = Graph()
c1 = Node("c1", (249.2, 57.9))
ctr = Node("tr", (287.5, 57.9))
c2 = Node("c2", (249.2, 197.8))
cr2 = Node("cr2", (287.5, 197.8))
c3 = Node("c3", (249.2, 318.7))
cr3 = Node("cr3", (287.5, 318.7))

c4 = Node("c4", (252.2, 459.9))
c5 = Node("c5", (252.8, 555.5))
c6 = Node("c6", (253.3, 658.4))
c7 = Node("c7", (256, 795))

r1 = Node("r1", (487.0, 318.4))
r2 = Node("r2", (321.9, 489.1))
r3 = Node("r3", (142.1, 670.9))

r1r = Node("r1r", (524.5, 355.4))
r2r = Node("r2r", (176.6, 707.3))

t1 = Node("t1", (351.6, 493.7))
t2 = Node("t2", (370.6, 510.0))
t3 = Node("t3", (326.0, 519.3))
t4 = Node("t4", (344.6, 543.9))
t5 = Node("t5", (294.9, 555.5))
t6 = Node("t6", (319.5, 578.8))
t7 = Node("t7", (294.9, 624.3))
t8 = Node("t8", (319.0, 615.5))
t9 = Node("t9", (292.1, 659.2))
t10 = Node("t10", (336.2, 635.5))
t11 = Node("t11", (293.5, 703.8))
t12 = Node("t12", (320.4, 703.8))
t13 = Node("t13", (398.5, 697.7))

t14 = Node("t14", (294.4, 795))

nodes = [c1, ctr, c2, cr2, c3, cr3, c4, c5, c6, c7, r1, r2,
         r3, r1r, r2r, t1, t2, t3, t4, t5, t6, t7, t8,
         t9, t10, t11, t12, t13, t14]

for node in nodes:
    graph.add_node(node)

graph.add_edge(c1, ctr)
graph.add_edge(c1, c2)
graph.add_edge(ctr, cr2)
graph.add_edge(cr2, cr3)
graph.add_edge(c2, cr2)
graph.add_edge(c2, c3)
graph.add_edge(c3, cr3)
graph.add_edge(c3, c4)
graph.add_edge(cr3, r2)
graph.add_edge(c4, c5)
graph.add_edge(c5, c6)
graph.add_edge(c5, r3)
graph.add_edge(c6, c7)
graph.add_edge(r3, r2r)
graph.add_edge(c5, r2)
graph.add_edge(r1, r2)
graph.add_edge(r1, r1r)
graph.add_edge(r1r, t2)
graph.add_edge(t2, t1)
graph.add_edge(t1, t3)
graph.add_edge(t3, t4)
graph.add_edge(t2, t4)
graph.add_edge(r2, t3)
graph.add_edge(t3, t5)
graph.add_edge(t5, t6)
graph.add_edge(t4, t6)
graph.add_edge(t6, t8)
graph.add_edge(t5, t7)
graph.add_edge(t7, t8)
graph.add_edge(t8, t10)
graph.add_edge(t10, t13)
graph.add_edge(t10, t12)
graph.add_edge(t11, t12)
graph.add_edge(t7, t9)
graph.add_edge(t11, t9)
graph.add_edge(t11, t14)
graph.add_edge(c6, t9)
graph.add_edge(c7, t14)
graph.add_edge(c6, r2r)

fig, ax = plt.subplots()
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

for node in graph.nodes:
    circle = plt.Circle(node.pos, radius=4, facecolor="r", linewidth=1, edgecolor="k", zorder=10)
    #plt.text(node.pos[0], node.pos[1], node.name, zorder=20)
    ax.add_artist(circle)

lines = {}
for edge in graph.edges:
    edges = list(edge)
    line = ax.plot([edges[0].pos[0], edges[1].pos[0]], [edges[0].pos[1], edges[1].pos[1]], lw=2, color="gray")
    lines[frozenset({edges[0],edges[1]})] = line[0]

sat = image.imread("../../images/sat_img.PNG")
plt.imshow(sat)

START = t13
GOAL = c1
came_from, cost_so_far = a_star_search(graph, START, GOAL)
path = reconstruct_path(came_from, START, GOAL)

from shapely.geometry import LineString
from shapely.ops import unary_union

n = 50
line = LineString(list(map(lambda x: x.pos, path)))

distances = np.linspace(0, line.length, n)
points = [line.interpolate(distance) for distance in distances]

import csv
with open("../../data/a_star_waypoints.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["X-axis","Y-axis"])
    for point in points:
        writer.writerow([point.x, point.y])

"""

frame_section = 60/(len(path)-1)

def update(frame):
    section = int(frame/frame_section)
    if frame == 0:
        for key in list(lines.keys()):
            lines[key].set_color("gray")

    if section < len(path)-1:
        lines[frozenset({path[section], path[section+1]})].set_color("red")

animation = ani.FuncAnimation(fig=fig, func=update, frames=60, interval=120)
#writer = PillowWriter(fps=15,metadata=dict(artist='Me'),bitrate=1800)
#animation.save('search.gif', writer=writer)
plt.tight_layout()
plt.show()
"""
