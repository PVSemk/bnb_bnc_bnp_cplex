import logging
from collections import defaultdict

import networkx as nx
import numpy as np


class ColoringHeuristic:
    def __init__(self, graph, growth_ratio=0.05, log=True):
        self.graph = graph
        self.strategies = [
            nx.coloring.strategy_largest_first,
            nx.coloring.strategy_connected_sequential_bfs,
            nx.coloring.strategy_connected_sequential_dfs,
            nx.coloring.strategy_saturation_largest_first,
            nx.coloring.strategy_smallest_last,
            nx.coloring.strategy_independent_set,
        ]
        self.strategy_random = nx.coloring.strategy_random_sequential
        self.growth_ratio = growth_ratio
        self.log = log

    def solve(self):
        def build_maximal_independent_set(colors_dict):
            for node, color in colors_dict.items():
                ind_sets_dict[color].append(node)
            for _, ind_set in ind_sets_dict.items():
                if len(ind_set) > 1:
                    ind_set = nx.algorithms.mis.maximal_independent_set(
                        self.graph, nodes=ind_set,
                    )
                    independent_sets.add(tuple(sorted(ind_set)))

        independent_sets = set()
        iterations_number = 0
        for strategy in self.strategies:
            ind_sets_dict = defaultdict(list)
            colors_dict = nx.coloring.greedy_color(self.graph, strategy=strategy)
            build_maximal_independent_set(colors_dict)
        while True:
            iterations_number += 1
            independent_sets_number = len(independent_sets)
            if len(independent_sets) == 0:
                break
            ind_sets_dict = defaultdict(list)
            colors_dict = nx.coloring.greedy_color(
                self.graph, strategy=self.strategy_random,
            )
            build_maximal_independent_set(colors_dict)
            if (len(independent_sets) - independent_sets_number) / len(
                independent_sets,
            ) < self.growth_ratio:
                if self.log:
                    logging.info(
                        f"Searched for independent sets during {iterations_number} iterations",
                    )
                break
        return list(independent_sets)

    def __call__(self):
        return self.solve()


class ViolatedContraintsHeuristic:
    def __init__(self, graph, iterations_limit=10, top_k=5):
        self.graph = graph
        self.epsilon = 1e-6
        self.iterations_limit = iterations_limit
        self.top_k = top_k

    def solve(self, dual_solution):
        dual_solution = np.array(dual_solution)
        dual_solution[np.abs(dual_solution) < self.epsilon] = 0
        # not_deleted_mask = np.ones(solution.shape, np.bool)
        # Randomized smallest degree last for weighted independent sets searching
        vertices_indices, weighted_degree = np.array(self.graph.degree()).T
        weighted_degree = dual_solution * weighted_degree
        sorted_nodes = vertices_indices[(np.argsort(weighted_degree)[::-1])].tolist()
        best_violated_constraints = set()
        best_total_weight = 1
        for _ in range(self.iterations_limit):
            violated_constraint = []
            sorted_nodes_copy = sorted_nodes.copy()
            total_weight = 0
            while len(sorted_nodes_copy) > 0:
                random_index = np.random.randint(
                    0, min(self.top_k, len(sorted_nodes_copy)),
                )
                current_node = sorted_nodes_copy[random_index]
                total_weight += dual_solution[current_node]
                violated_constraint.append(current_node)
                node_neighbours = self.graph[current_node].keys()
                # print(list(node_neighbours))
                sorted_nodes_copy.pop(random_index)
                sorted_nodes_copy = list(
                    filter(lambda x: x in node_neighbours, sorted_nodes_copy),
                )
            if total_weight > best_total_weight + self.epsilon:
                violated_constraint = sorted(violated_constraint)
                if tuple(violated_constraint) in best_violated_constraints:
                    break
                best_violated_constraints.add(tuple(violated_constraint))
                # best_total_weight = total_weight
        if len(best_violated_constraints):
            return best_violated_constraints, None
        else:
            return None, None

    def __call__(self, dual_solution):
        return self.solve(dual_solution)
