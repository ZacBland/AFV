from search import Graph, Node
import json

with open('../logs/airport_test.json') as file:
    data = json.load(file)

graph = Graph.from_dict(data)

from search.a_star import a_star_search, reconstruct_path
n2 = graph.nodes[0]
n1 = graph.get_node_from_name("68")
print(n1.name)
print(n2.name)
print(graph.get_neighbors(n1))

came_from, cost_so_far = a_star_search(graph, n1, n2)
path = reconstruct_path(came_from, n1, n2)


print("done")
for node in path:
    print(node.name)
