import csv

start_x = 0.0
start_y = 0.0

goal_x = 100.0
goal_y = 100.0

up_points = left_points = 25

y_step = goal_y/up_points
x_step = goal_x/left_points


with open("../data/test.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["X-axis","Y-axis"])

    for i in range(up_points):
        writer.writerow([start_x, start_y+i*y_step])

    for i in range(left_points):
        writer.writerow([start_x+i*x_step, goal_y])

