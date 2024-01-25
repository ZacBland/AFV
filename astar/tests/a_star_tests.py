import unittest
from ..a_star import *

class TestStringMethods(unittest.TestCase):

    def test_cell(self):
        cell = Cell(5)
        self.assertEqual(cell.weight(), 5)

    def test_grid_size(self):
        rows = 10
        grid = Grid(rows, 15)
        self.assertEqual(len(grid), 10)
        for i in range(0, rows):
            self.assertEqual(len(grid[i]), 15)

    def test_cell_neighbors(self):

        rows = 100
        cols = 100
        grid = Grid(rows, cols)

        cell_x = 50
        cell_y = 50
        cell = grid[cell_y][cell_x]
        neighbors = grid.neighbors((cell_y, cell_x))
        left = neighbors["left"]
        right = neighbors["right"]
        up = neighbors["up"]
        down = neighbors["down"]

        c_left = grid[cell_y][cell_x - 1]
        c_right = grid[cell_y][cell_x + 1]
        c_up = grid[cell_y - 1][cell_x]
        c_down = grid[cell_y + 1][cell_x]

        self.assertEqual(c_left, left)
        self.assertEqual(c_right, right)
        self.assertEqual(c_up, up)
        self.assertEqual(c_down, down)

    def test_generation_time(self):
        rows = 50000
        cols = 50000
        grid = Grid(rows, cols)

if __name__ == '__main__':
    unittest.main()