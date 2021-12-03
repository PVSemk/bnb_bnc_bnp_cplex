import logging
from collections import defaultdict
from math import floor
from time import time

import cplex
import networkx as nx
import networkx.algorithms.mis
import numpy as np

from utils import check_clique, time_it


class CliqueSolver:
    def __init__(self, graph, time_limit, debug=False):
        self.graph = graph
        self.complement_graph = nx.complement(self.graph)
        self.debug = debug
        self.n_independent_sets_growth_ratio = 0.1
        self.timer = time()
        self.time_limit = time_limit
        self.problem = self.construct_problem()[0]  # time_it returns time additionally

    @time_it
    def construct_problem(self):
        problem = cplex.Cplex()
        if not self.debug:
            problem.set_log_stream(None)
            problem.set_results_stream(None)
            problem.set_warning_stream(None)
            problem.set_error_stream(None)

        problem.objective.set_sense(problem.objective.sense.maximize)
        type_one = 1.0
        type_zero = 0.0
        var_type = problem.variables.type.continuous
        num_nodes = self.graph.number_of_nodes()
        obj = [type_one] * num_nodes
        upper_bounds = [type_one] * num_nodes
        lower_bounds = [type_zero] * num_nodes
        types = zip(range(num_nodes), [var_type] * num_nodes)
        columns_names = [f"x{x}" for x in range(num_nodes)]
        independent_sets = self.get_independent_sets()

        problem.variables.add(
            obj=obj, ub=upper_bounds, lb=lower_bounds, names=columns_names,
        )
        problem.variables.set_types(types)

        constraints = []
        for ind_set in independent_sets:
            constraints.append([[f"x{i}" for i in ind_set], [type_one] * len(ind_set)])

        contstraints_length = len(constraints)
        right_hand_side = [type_one] * contstraints_length
        constraint_names = [f"c{i}" for i in range(contstraints_length)]
        constraint_senses = ["L"] * contstraints_length

        problem.linear_constraints.add(
            lin_expr=constraints,
            senses=constraint_senses,
            rhs=right_hand_side,
            names=constraint_names,
        )
        return problem

    def get_independent_sets(self):
        def build_maximal_independent_set(colors_dict):
            for node, color in colors_dict.items():
                ind_sets_dict[color].append(node)
            for _, ind_set in ind_sets_dict.items():
                if len(ind_set) > 1:
                    ind_set = networkx.algorithms.mis.maximal_independent_set(
                        self.graph, nodes=ind_set,
                    )
                    independent_sets.add(tuple(sorted(ind_set)))

        independent_sets = set()
        strategies = [
            nx.coloring.strategy_largest_first,
            nx.coloring.strategy_connected_sequential_bfs,
            nx.coloring.strategy_connected_sequential_dfs,
            nx.coloring.strategy_saturation_largest_first,
            nx.coloring.strategy_smallest_last,
            nx.coloring.strategy_independent_set,
        ]
        strategy_random = nx.coloring.strategy_random_sequential
        iterations_number = 0
        for strategy in strategies:
            ind_sets_dict = defaultdict(list)
            colors_dict = nx.coloring.greedy_color(self.graph, strategy=strategy)
            build_maximal_independent_set(colors_dict)
        while True:
            if time() - self.timer >= self.time_limit * 0.1:
                logging.info("Out of time for independent sets searching")
                break
            iterations_number += 1
            independent_sets_number = len(independent_sets)
            if len(independent_sets) == 0:
                break
            ind_sets_dict = defaultdict(list)
            colors_dict = nx.coloring.greedy_color(self.graph, strategy=strategy_random)
            build_maximal_independent_set(colors_dict)
            if (len(independent_sets) - independent_sets_number) / len(
                independent_sets,
            ) < self.n_independent_sets_growth_ratio:
                logging.info(
                    f"Searched for independent sets during {iterations_number} iterations",
                )
                break
        return list(independent_sets)

    def solve(self):
        self.problem.solve()
        solution = self.problem.solution.get_values()
        objective_value = self.problem.solution.get_objective_value()
        return solution, objective_value

    @time_it
    def __call__(self):
        return self.solve()

    def get_solution(self):
        return self.problem.solution.get_values()

    def get_objective_value(self):
        return self.problem.solution.get_objective_value()

    def check_time(self):
        if time() - self.timer >= self.time_limit:
            raise TimeoutError


class BnCCliqueSolver(CliqueSolver):
    def __init__(self, graph, time_limit, debug=False):
        super().__init__(graph, time_limit, debug)
        self.best_found_clique_size = 0
        self.best_solution = None
        self.branch_idx = 0
        self.cut_idx = 0
        self.epsilon = 1e-6
        self.branching_set = set()
        self.added_constraints_size = 0
        self.call_times = 0
        self.contrained_variables = np.zeros(self.graph.number_of_nodes())
        self.tolerance_limit = 5
        self.cutting_iterations_number = 10

    def add_branching_constraint(self, variable, rhs, branch_idx):
        self.problem.linear_constraints.add(
            lin_expr=[[[f"x{variable}"], [1.0]]],
            senses=["E"],
            rhs=[rhs],
            names=[f"branch_{branch_idx}"],
        )

    def add_cutting_constraint(self, variables):
        names = [f"x{i}" for i in variables]
        lin_expr = [names, [1.0] * len(variables)]

        self.problem.linear_constraints.add(
            lin_expr=[lin_expr], senses=["L"], rhs=[1.0], names=[f"cut_{self.cut_idx}"],
        )

    def delete_branching_constraint(self, branch_idx):
        self.problem.linear_constraints.delete(f"branch_{branch_idx}")

    # We take the variable which is the closest to 1 as branching variable
    def find_branching_variable(self, solution):
        equals_one = np.isclose(solution, 1.0, atol=self.epsilon)
        equals_zero = np.isclose(solution, 0.0, atol=self.epsilon)
        integer_var = equals_zero | equals_one
        if np.all(integer_var):
            return None
        else:
            return np.argmax(
                np.where(~equals_one, solution, -1),
            )  # Variables equal to 1 are set to -1 (we don't want to take them)

    def separation(self, solution, top_k=5):
        solution = np.array(solution)
        solution[np.abs(solution) < self.epsilon] = 0
        not_deleted_mask = np.ones(solution.shape, np.bool)
        # Randomized smallest degree last for weighted independent sets searching
        graph = self.complement_graph.copy()
        sorted_nodes = []
        while graph.number_of_nodes():
            vertices_indices, weighted_degree = np.array(graph.degree()).T
            weighted_degree = solution[not_deleted_mask] * weighted_degree
            min_degree_vertex_idx = np.argmin(weighted_degree)
            sorted_nodes.append(
                (
                    vertices_indices[min_degree_vertex_idx],
                    solution[not_deleted_mask][min_degree_vertex_idx],
                ),
            )
            graph.remove_node(sorted_nodes[-1][0])
            not_deleted_mask[sorted_nodes[-1][0]] = False
        sorted_nodes = list(reversed(sorted_nodes))
        best_violated_constraints = set()
        best_total_weight = 1
        for _ in range(self.cutting_iterations_number):
            violated_constraint = []
            sorted_nodes_copy = sorted_nodes.copy()
            total_weight = 0
            while len(sorted_nodes_copy) > 0:
                random_index = np.random.randint(0, min(top_k, len(sorted_nodes_copy)))
                current_node = sorted_nodes_copy[random_index][0]
                total_weight += sorted_nodes_copy[random_index][1]
                violated_constraint.append(current_node)
                node_neighbours = list(self.complement_graph.neighbors(current_node))
                sorted_nodes_copy.pop(random_index)
                sorted_nodes_copy = list(
                    filter(lambda x: x[0] in node_neighbours, sorted_nodes_copy),
                )
            if total_weight - best_total_weight > self.epsilon:
                best_violated_constraints.add(tuple(violated_constraint))
                best_total_weight = total_weight
        if len(best_violated_constraints):
            return best_violated_constraints
        else:
            return None

    def call_solver(self):
        try:
            solution, objective_value = super().solve()
        except cplex.exceptions.CplexSolverError:
            return None, None
        return solution, objective_value

    def find_errors_in_candidate_clique(self, solution):
        clique_nodes = np.where(np.isclose(solution, 1.0, atol=self.epsilon))[0]
        violated_constraints_candidate = self.complement_graph.subgraph(
            clique_nodes,
        ).edges
        violated_constraints = set()
        for edge in violated_constraints_candidate:
            violated_constraints.add(
                tuple(networkx.maximal_independent_set(self.graph, edge)),
            )  # ToDo: possibly, rewrite to own implementation
        return violated_constraints

    def remove_non_binding_constraints(self):
        # return
        removed_constraints = 0
        names = self.problem.linear_constraints.get_names()
        non_binding_constraints = np.nonzero(
            ~np.isclose(
                self.problem.solution.get_linear_slacks(), 0.0, atol=self.epsilon,
            ),
        )[0]
        for constraint_ix in non_binding_constraints:
            name = names[constraint_ix]
            if "branch_" not in name:
                removed_constraints += 1
                self.problem.linear_constraints.delete(name)
        logging.info(
            f"Removed {removed_constraints} non-binding constraints, "
            f"remained {self.problem.linear_constraints.get_num()} constraints",
        )

    def solve(self):
        self.call_times += 1
        self.check_time()
        solution, objective_value = self.call_solver()
        if self.call_times == 1:  # Initial removing of non binding contraints
            self.remove_non_binding_constraints()
        if solution is None:
            return 0
        if floor(objective_value + self.epsilon) <= self.best_found_clique_size:
            return 0

        if self.call_times % 200 == 0:
            logging.info(
                f"Total Call times: {self.call_times}, Best Found Solution: {self.best_found_clique_size},"
                f"Current Solution: {objective_value}",
            )
            logging.info(
                f"Number of constrained variables: {self.added_constraints_size}",
            )
        if self.call_times % 2000 == 0:
            self.remove_non_binding_constraints()
        tolerance_counter = 0
        previous_objective_value = objective_value
        while True:
            most_violated_constraints = self.separation(solution)
            if most_violated_constraints is None:
                break
            for most_violated_constraint in most_violated_constraints:
                self.add_cutting_constraint(most_violated_constraint)
                self.cut_idx += 1
            solution, objective_value = self.call_solver()
            if solution is None:
                return 0
            if floor(objective_value + self.epsilon) <= self.best_found_clique_size:
                return 0
            if previous_objective_value - objective_value < 0.1:
                tolerance_counter += 1
            else:
                previous_objective_value = objective_value
                tolerance_counter = 0

            if tolerance_counter == self.tolerance_limit:
                break

        branching_variable = self.find_branching_variable(solution)

        if branching_variable is None:
            if not check_clique(self.graph, solution)[0]:
                violated_contraints = self.find_errors_in_candidate_clique(solution)
                for violated_constraint in violated_contraints:
                    self.add_cutting_constraint(violated_constraint)
                    self.cut_idx += 1
                self.solve()
            else:
                self.best_found_clique_size = objective_value
                self.best_solution = solution
        else:
            for branch_value in [1.0, 0.0]:
                self.branch_idx += 1
                current_branch = self.branch_idx
                self.added_constraints_size += 1
                self.add_branching_constraint(
                    branching_variable, branch_value, current_branch,
                )
                self.solve()
                self.delete_branching_constraint(current_branch)
                self.added_constraints_size -= 1
        return 0

    def get_solution(self):
        return self.best_solution

    def get_objective_value(self):
        return self.best_found_clique_size

    def set_objective_value(self, objective_value):
        self.best_found_clique_size = objective_value

    def set_solution(self, solution):
        self.best_solution = solution
