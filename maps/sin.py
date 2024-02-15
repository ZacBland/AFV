import numpy as np
import math

def func(x):
    return 100*math.sin(.01*x)

if __name__ == "__main__":
    x = np.linspace(0.1,1000,100)
    y = list(map(lambda x: func(x), x))
    points = zip(x, y)

    import csv

    with open("../data/sin.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["X-axis", "Y-axis"])
        for point in points:
            writer.writerow([point[0], point[1]])