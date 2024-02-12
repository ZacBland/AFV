from __future__ import annotations
from libs.defines import *
from typing import *
import math


class Node:
    def __init__(self, name: str, pos: Location):
        self.name = name
        self.pos = pos

    def __str__(self):
        return self.name


class Graph:
    def __init__(self, nodes: List[Node, ...] = None, edges: Dict[Set[Node, Node], float] = None):
        """
        Initialize Graph Object.
        :param nodes: List of Nodes
        :param edges: Dict of Edges with cost, ex: {(A, B), 3}
        """
        if nodes is None:
            nodes = []
        self.nodes = nodes
        if edges is None:
            edges = {}
        self.edges = edges

    def add_node(self, node: Node):
        """
        Add node to node list
        :param node: Node
        """
        if node in self.nodes:
            print(f"Node {node.name} already in Graph")
            return
        self.nodes.append(node)

    def remove_node(self, node: Node):
        """
        Remove Node from Node List
        :param node: Node
        """
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            print("Node not in Graph")

    def get_node(self, pos: Location):
        """
        Get node from position tuple
        :param pos: Location: Tuple(float, float)
        :return: Node
        """
        for node in self.nodes:
            if node.pos == pos:
                return node
        print(f"Node with position {pos} not found.")

    def get_neighbors(self, node: Node):
        """
        Returns neighbors of given node
        :param node:
        :return:
        """
        neighbors = []
        for key in list(self.edges.keys()):
            if node in key:
                other = list(key.difference({node}))[0]
                neighbors.append(other)
        return neighbors

    def add_edge(self, a: Node, b: Node, cost=None):
        """
        Adds edge between two given nodes
        :param a: Node A
        :param b: Node b
        :param cost: Cost value
        """
        if cost is None:
            cost = math.sqrt((b.pos[0] - a.pos[0])**2 + (b.pos[1] - a.pos[1])**2)
        if {a, b} not in list(self.edges.keys()):
            self.edges[frozenset({a, b})] = cost
        else:
            print("Edge already exists.")

    def change_cost(self, a: Node, b: Node, cost=1):
        if {a, b} in list(self.edges.keys()):
            self.edges[frozenset({a, b})] = cost
        else:
            print("Edge not found.")

    def get_cost(self, a: Node, b: Node):
        if {a, b} in list(self.edges.keys()):
            return self.edges[frozenset({a,b})]
        else:
            print("Edge not found.")



