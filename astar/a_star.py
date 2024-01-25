from __future__ import annotations
from typing import *
import numpy as np
from queue import PriorityQueue
import random

Location = TypeVar('Location')
class Cell:

    def __init__(self, weight=1):
        #Set Weight of Cell
        self._weight = weight

        #Initialize Neighbor Cells
        self._right = None
        self._left = None
        self._up = None
        self._down = None

    def weight(self) -> int:
        return self._weight

    def set_left(self, cell: Cell):
        self._left = cell
    def set_right(self, cell: Cell):
        self._right = cell
    def set_down(self, cell: Cell):
        self._down = cell
    def set_up(self, cell: Cell):
        self._up = cell

    @property
    def left(self) -> Cell:
        return self._left

    @property
    def right(self) -> Cell:
        return self._right

    @property
    def up(self) -> Cell:
        return self._up

    @property
    def down(self) -> Cell:
        return self._down

class Grid:

    def __init__(self, rows=20, cols=20):
        self._rows = rows
        self._cols = cols
        self._grid = np.ones((self._rows, self._cols))
        for i in range(rows):
            for j in range(cols):
                self._grid[i][j] = random.randint(1,100)

    def neighbors(self, pos) -> list:
        (i,j) = pos
        left = None
        right = None
        up = None
        down = None
        if j - 1 >= 0:
            left = (i,j-1)
        if j + 1 < self._cols:
            right = (i,j+1)
        if i - 1 >= 0:
            up = (i-1,j)
        if i + 1 < self._rows:
            down = (i+1,j)
        return [right, left, up, down]

    def cost(self, pos):
        (i,j) = pos
        return self._grid[i][j]

    def __getitem__(self, index):
        return self._grid[index]

    def __len__(self):
        return len(self._grid)


def heuristic(a: tuple, b: tuple) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(grid, start, goal):
    frontier = PriorityQueue()
    frontier.put((start,0))
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: Location = frontier.get()[0]

        if current == goal:
            break

        for next in grid.neighbors(current):
            if next is None:
                continue
            new_cost = cost_so_far[current] + grid.cost(next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(next, goal)
                frontier.put((next, priority))
                came_from[next] = current
    return came_from, cost_so_far


def reconstruct_path(came_from: dict[Location, Location], start: Location, goal: Location) -> list[Location]:
    current: Location = goal
    path: list[Location] = []
    if goal not in came_from: # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path

if __name__ == "__main__":
    start = (0, 0)
    goal = (9, 9)
    grid = Grid(10, 10)
    came_from, cost_so_far = a_star_search(grid, start, goal)
    print(reconstruct_path(came_from, start, goal))

