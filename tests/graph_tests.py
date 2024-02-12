import unittest
from search.graph import *
from search.a_star.a_star import *


class TestGraphClass(unittest.TestCase):

    def test_neighbors(self):
        graph = Graph()
        node_a = Node("A", (0, 0))
        node_b = Node("B", (1, 1))
        node_c = Node("C", (0, 1))

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)

        graph.add_edge(node_a, node_b, 1)
        graph.add_edge(node_a, node_c, 2)
        graph.add_edge(node_b, node_c, 4)

        neighbors = graph.get_neighbors(node_a)
        for neighbor in neighbors:
            self.assertNotEqual(neighbor[0], node_a)

    def test_change_cost(self):
        graph = Graph()
        node_a = Node("A", (0, 0))
        node_b = Node("B", (1, 1))
        node_c = Node("C", (0, 1))

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)

        graph.add_edge(node_a, node_b, 1)

        graph.change_cost(node_a, node_b, 2)

        print(graph.edges)

    def test_a_star_graph(self):
        graph = Graph()
        node_a = Node("A", (0, 0))
        node_b = Node("B", (1, 1))
        node_c = Node("C", (0, 1))

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)

        graph.add_edge(node_a, node_b, 1)
        graph.add_edge(node_b, node_c, 1)

        came_from, cost_so_far = a_star_search(graph, node_a, node_c)
        path = reconstruct_path(came_from, node_a, node_c)
        name_path = list(map(lambda x: x.name, path))
        print(name_path)

    def test_get_cost(self):
        graph = Graph()
        node_a = Node("A", (0, 0))
        node_b = Node("B", (1, 1))
        node_c = Node("C", (0, 1))

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)

        graph.add_edge(node_a, node_b, 1)

        print(graph.get_cost(node_a, node_b))

    def test_a_star_visual(self):
        import matplotlib.pyplot as plt
        import numpy as np

        graph = Graph()
        node_a = Node("A", (0, 0))
        node_b = Node("B", (1, 1))
        node_c = Node("C", (0, 1))

        graph.add_node(node_a)
        graph.add_node(node_b)
        graph.add_node(node_c)

        graph.add_edge(node_a, node_b, 1)
        graph.add_edge(node_a, node_c, 2)
        graph.add_edge(node_b, node_c, 4)

        fig, ax = plt.subplots()


        for node in graph.nodes:
            circle = plt.Circle(node.pos, radius=0.1,facecolor="r", linewidth=1, edgecolor="k", zorder=10)
            ax.add_artist(circle)

        for edge in graph.edges:
            nodes = list(edge)
            ax.plot([nodes[0].pos[0], nodes[1].pos[0]], [nodes[0].pos[1], nodes[1].pos[1]], lw=2, color="gray")


        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2])
        fig.show()




if __name__ == '__main__':
    unittest.main()