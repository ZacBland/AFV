from a_star import *
import pygame as pyg
import sys
import time

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WINDOW_HEIGHT = 500
WINDOW_WIDTH = 500
ROWS = 10
COLS = 10


def main():
    global SCREEN, CLOCK, GRID, COLORS
    GRID = []
    pyg.init()
    SCREEN = pyg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pyg.time.Clock()
    SCREEN.fill(BLACK)

    timer_interval = 500
    timer_event = pyg.USEREVENT+1
    pyg.time.set_timer(timer_event, timer_interval)

    (start_x, start_y) = START
    (goal_x, goal_y) = GOAL

    COLORS = []
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            row.append((0, 255-(WEIGHTS[i][j]*2), 0))
        COLORS.append(row)

    COLORS[start_x][start_y] = RED
    COLORS[goal_x][goal_y] = RED

    clear_list = []

    i = 1
    while True:
        CLOCK.tick(60)

        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                sys.exit()
            if event.type == timer_event:
                x = PATH[i][0]
                y = PATH[i][1]
                COLORS[x][y] = RED
                clear_list.append((x,y))
                i += 1
                if i % len(PATH) == 0:
                    for (x,y) in clear_list:
                        COLORS[x][y] = (0, 255-(WEIGHTS[x][y]*2), 0)
                i = i % len(PATH)

        drawGrid()
        pyg.display.update()

def drawGrid():
    spacing = 1

    block_width = int(WINDOW_HEIGHT/ROWS)
    block_height = int(WINDOW_HEIGHT/COLS)


    for x in range(ROWS):
        g = []
        for y in range(COLS):
            rect = pyg.Rect(x*block_width+spacing, y*block_height+spacing, block_width-spacing, block_height-spacing)
            r = pyg.draw.rect(SCREEN, COLORS[x][y], rect)
            fontTitle = pyg.font.SysFont("arial", 10)
            textTitle = fontTitle.render(str(WEIGHTS[x][y]), True, BLACK)
            SCREEN.blit(textTitle, rect)
            g.append(r)
        GRID.append(g)


if __name__ == "__main__":
    global PATH, GOAL, START, WEIGHTS
    START = (0, 0)
    GOAL = (9, 9)
    WEIGHTS = Grid(ROWS, COLS)
    came_from, cost_so_far = a_star_search(WEIGHTS, START, GOAL)
    PATH = reconstruct_path(came_from, START, GOAL)

    main()