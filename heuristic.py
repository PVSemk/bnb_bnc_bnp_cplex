import numpy as np

from utils import read_graph


class GreedyHeuristic:
    def __init__(self, graph, iterations_number=150, top_k=5):
        self.graph = graph
        self.strategies = [
            self.largest_first,
            self.largest_first_randomized,
            self.smallest_degree_last_with_remove,
            self.smallest_degree_last_with_remove_randomized,
        ]
        self.top_k = top_k
        self.iterations_number = iterations_number

    def solve(self):
        best_clique = 0
        best_solution = None
        for strategy in self.strategies:
            found_clique = strategy()
            if len(found_clique) > best_clique:
                best_clique = len(found_clique)
                best_solution = found_clique
        nodes_solution = np.zeros(self.graph.number_of_nodes())
        nodes_solution[best_solution] = 1
        return nodes_solution, len(best_solution)

    def __call__(self):
        return self.solve()

    def largest_first(self):
        solution = []
        sorted_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)
        while len(sorted_nodes) > 0:
            current_node = sorted_nodes[0][0]
            solution.append(current_node)
            node_neighbours = list(self.graph.neighbors(current_node))
            sorted_nodes.pop(0)
            sorted_nodes = list(filter(lambda x: x[0] in node_neighbours, sorted_nodes))
        return solution

    def largest_first_randomized(self):
        best_solution = None
        best_clique = 0
        sorted_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)
        for _ in range(self.iterations_number):
            solution = []
            sorted_nodes_copy = sorted_nodes.copy()
            while len(sorted_nodes_copy) > 0:
                random_index = np.random.randint(
                    0, min(self.top_k, len(sorted_nodes_copy)),
                )
                current_node = sorted_nodes_copy[random_index][0]
                solution.append(current_node)
                node_neighbours = list(self.graph.neighbors(current_node))
                sorted_nodes_copy.pop(random_index)
                sorted_nodes_copy = list(
                    filter(lambda x: x[0] in node_neighbours, sorted_nodes_copy),
                )
            if len(solution) > best_clique:
                best_solution = solution
                best_clique = len(solution)
        return best_solution

    def smallest_degree_last_with_remove(self):
        solution = []
        graph = self.graph.copy()
        sorted_nodes = []
        while graph.number_of_nodes():
            sorted_nodes.append(min(graph.degree(), key=lambda x: x[1]))
            graph.remove_node(sorted_nodes[-1][0])
        sorted_nodes = list(reversed(sorted_nodes))
        while len(sorted_nodes) > 0:
            current_node = sorted_nodes[0][0]
            solution.append(current_node)
            node_neighbours = list(self.graph.neighbors(current_node))
            sorted_nodes.pop(0)
            sorted_nodes = list(filter(lambda x: x[0] in node_neighbours, sorted_nodes))
        return solution

    def smallest_degree_last_with_remove_randomized(self):
        best_solution = None
        best_clique = 0
        sorted_nodes = []
        graph = self.graph.copy()
        while graph.number_of_nodes():
            sorted_nodes.append(min(graph.degree(), key=lambda x: x[1]))
            graph.remove_node(sorted_nodes[-1][0])
        sorted_nodes = list(reversed(sorted_nodes))
        for _ in range(self.iterations_number):
            solution = []
            sorted_nodes_copy = sorted_nodes.copy()
            while len(sorted_nodes_copy) > 0:
                random_index = np.random.randint(
                    0, min(self.top_k, len(sorted_nodes_copy)),
                )
                current_node = sorted_nodes_copy[random_index][0]
                solution.append(current_node)
                node_neighbours = list(self.graph.neighbors(current_node))
                sorted_nodes_copy.pop(random_index)
                sorted_nodes_copy = list(
                    filter(lambda x: x[0] in node_neighbours, sorted_nodes_copy),
                )
            if len(solution) > best_clique:
                best_solution = solution
                best_clique = len(solution)
        return best_solution


def test_heuristic():
    graph = read_graph("./DIMACS_all_ascii/c-fat200-1.clq")
    heuristic = GreedyHeuristic(graph)
    found_clique, found_clique_size = heuristic.solve()
    print(f"Found clique: {found_clique_size}")


if __name__ == "__main__":
    test_heuristic()
