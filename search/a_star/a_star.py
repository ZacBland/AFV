from typing import *
from queue import PriorityQueue
from search.graph import Node, Graph
from math import sqrt


def heuristic(a: Node, b: Node) -> float:
    return int(sqrt((b.pos[0] - a.pos[0])**2 + (b.pos[1] - a.pos[1])**2))


def a_star_search(graph: Graph, start: Node, goal: Node):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from: dict[Node, Optional[Node]] = {}
    cost_so_far: dict[Node, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: Node = frontier.get()[1]

        if current == goal:
            break

        for neighbor in graph.get_neighbors(current):
            if neighbor is None:
                continue
            new_cost = cost_so_far[current] + graph.get_cost(current, neighbor)
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                frontier.put((priority, neighbor))
                came_from[neighbor] = current
    return came_from, cost_so_far


def reconstruct_path(came_from: dict[Node, Node], start: Node, goal: Node) -> list[Node]:
    current: Node = goal
    path: list[Node] = []
    if goal not in came_from:
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path
