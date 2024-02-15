import numpy as np
import math


if __name__ == "__main__":
    x = [0.0, 100.0, 100.0]
    y = [0.0, 0.0, 100.0]
    n = 1000


    from shapely.geometry import LineString
    from shapely.ops import unary_union

    line = LineString(zip(x, y))

    distances = np.linspace(0, line.length, n)
    points = [line.interpolate(distance) for distance in distances]
    points = [[point.x, point.y] for point in points]

    import csv

    with open("../data/sharp.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["X-axis", "Y-axis"])
        for point in points:
            writer.writerow([point[0], point[1]])