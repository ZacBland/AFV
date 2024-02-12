from __future__ import annotations
import numpy as np


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
