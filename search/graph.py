"""
5/10/24
Author: Zac Bland
"""

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

    @classmethod
    def from_dict(cls, dict):
        nodes_list = dict["Nodes"]
        edges_list = dict["Edges"]

        nodes = []
        edges = {}
        for n in nodes_list:
            nodes.append(Node(n[0], (n[1][0], n[1][1])))

        for e in edges_list:
            edges[frozenset([e[0], e[1]])] = None

        return cls(nodes=nodes, edges=edges)

    def __init__(self, nodes: List[Node, ...] = None, edges: Dict[Set[Node, Node], float] = None):
        """
        Initialize Graph Object.
        :param nodes: List of Nodes
        :param edges: Dict of Edges with cost, ex: {(A, B), 3}
        """
        if nodes is None:
            nodes = []
        self.nodes = nodes

        self.edges = {}
        if edges is not None:
            for key in list(edges.keys()):
                key_list = list(key)
                self.add_edge(self.get_node_from_name(key_list[0]), self.get_node_from_name(key_list[1]))

    def add_node(self, node: Node):
        """
        Add node to node list
        :param node: Node
        """
        for n in self.nodes:
            if node.name == n.name:
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
            self.remove_edge(node)
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

    def get_node_from_name(self, name: str):
        """
        Get node from name
        :param name: (str) Node name
        :return: Node
        """
        for node in self.nodes:
            if node.name == name:
                return node
        print(f"Node with name {name} not found.")

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

    def remove_edge(self, node: Node):
        for key in list(self.edges.keys()):
            if node in key:
                self.edges.pop(frozenset(key))


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

    def to_dict(self):
        json_dict = {}

        json_dict["Nodes"] = []
        for node in self.nodes:
            json_dict["Nodes"].append([node.name, node.pos])

        json_dict["Edges"] = []
        for edge in self.edges:
            edge_list = list(edge)
            json_dict["Edges"].append((edge_list[0].name, edge_list[1].name, self.get_cost(edge_list[0], edge_list[1])))

        return json_dict





