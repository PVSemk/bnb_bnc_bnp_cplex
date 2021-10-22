from time import time
from utils import cartesian_product, time_it
import cplex
import numpy as np
import networkx as nx
import logging
from math import floor
from utils import check_clique
from collections import defaultdict


class CliqueSolver:
    def __init__(self, graph, solve_type, time_limit, debug=False):
        assert solve_type in ["LP", "ILP"], "Solve type should be either LP or ILP"
        self.graph = graph
        self.solve_type = solve_type
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
        if self.solve_type == "LP":
            type_one = 1.0
            type_zero = 0.0
            var_type = problem.variables.type.continuous
        else:
            type_one = 1
            type_zero = 0
            var_type = problem.variables.type.binary
        num_nodes = self.graph.number_of_nodes()
        obj = [type_one] * num_nodes
        upper_bounds = [type_one] * num_nodes
        lower_bounds = [type_zero] * num_nodes
        types = zip(range(num_nodes), [var_type] * num_nodes)
        columns_names = [f'x{x}' for x in range(num_nodes)]
        not_connected = np.array(nx.complement(self.graph).edges)
        independent_sets = self.get_independent_sets()

        problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                              names=columns_names)
        problem.variables.set_types(types)

        constraints = []
        pairs_covered_by_independent_sets = list()
        for ind_set in independent_sets:
            constraints.append([[f'x{i}' for i in ind_set], [type_one] * len(ind_set)])
            pairs_covered_by_independent_sets.extend(cartesian_product(ind_set, ind_set))
        if len(pairs_covered_by_independent_sets):
            pairs_covered_by_independent_sets = np.asarray(pairs_covered_by_independent_sets)
            pairs_covered_by_independent_sets = np.unique(pairs_covered_by_independent_sets, axis=0)
            condition = pairs_covered_by_independent_sets[:, 0] == pairs_covered_by_independent_sets[:, 1]
            pairs_covered_by_independent_sets = np.delete(pairs_covered_by_independent_sets, np.where(condition), axis=0)
            not_connected = not_connected[~((not_connected[:, None, :] == pairs_covered_by_independent_sets).all(-1)).any(1)]  # Remove pairs covered by independent sets from not connected
        for xi, xj in not_connected:
            constraints.append(
                [[f'x{xi}', f'x{xj}'], [type_one, type_one]])



        contstraints_length = len(constraints)
        right_hand_side = [type_one] * contstraints_length
        constraint_names = [f'c{i}' for i in range(contstraints_length)]
        constraint_senses = ['L'] * contstraints_length

        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        return problem


    def get_independent_sets(self):
        independent_sets = set()
        strategies = [nx.coloring.strategy_largest_first,
                      nx.coloring.strategy_random_sequential,
                      nx.coloring.strategy_independent_set,
                      nx.coloring.strategy_connected_sequential_bfs,
                      nx.coloring.strategy_connected_sequential_dfs,
                      nx.coloring.strategy_saturation_largest_first,
                      nx.coloring.strategy_smallest_last
                      ]
        iterations_number = 0
        while (True):
            iterations_number += 1
            independent_sets_number = len(independent_sets)
            for strategy in strategies:
                ind_sets_dict = defaultdict(list)
                colors_dict = nx.coloring.greedy_color(self.graph, strategy=strategy)
                for node, color in colors_dict.items():
                    ind_sets_dict[color].append(node)
                for color, ind_set in ind_sets_dict.items():
                    if len(ind_set) > 2:
                        independent_sets.add(tuple(sorted(ind_set)))
            if (len(independent_sets) - independent_sets_number) / len(independent_sets) < self.n_independent_sets_growth_ratio:
                logging.info(f"Searched for independent sets during {iterations_number} iterations")
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


class BnBCliqueSolver(CliqueSolver):
    def __init__(self, graph, solve_type, time_limit, debug=False):
        super().__init__(graph, solve_type, time_limit, debug)
        self.best_found_clique_size = 0
        self.best_solution = None
        self.branch_idx = 0
        self.epsilon = 1e-3
        self.branching_set = set()
        self.added_constraints_size = 0
        self.call_times = 0
        self.contrained_variables = np.zeros(self.graph.number_of_nodes())

    def add_constraint(self, variable, rhs, branch_idx):
        self.problem.linear_constraints.add(lin_expr=[[[f"x{variable}"], [1.0]]],
                                            senses=["E"],
                                            rhs=[rhs],
                                            names=[f"branch_{branch_idx}"])

    def delete_constraint(self, branch_idx):
        self.problem.linear_constraints.delete(f"branch_{branch_idx}")

    # We take the variable which is the closest to 1 as branching variable
    def find_branching_variable(self, solution):
        equals_one = np.isclose(solution, 1.0, atol=self.epsilon)
        equals_zero = np.isclose(solution, 0.0, atol=self.epsilon)
        if np.all(equals_one | equals_zero):
            return None
        else:
            return np.argmax(np.where(~equals_one, solution,  -1)) # Variables equal to 1 are set to -1 (we don't want to take them)

    def check_time(self):
        if time() - self.timer >= self.time_limit:
            raise TimeoutError

    def solve(self):
        self.call_times += 1
        self.check_time()
        solution, objective_value = super().solve()
        if floor(objective_value + self.epsilon) <= self.best_found_clique_size:
            return 0

        if self.call_times % 2500 == 0:
            logging.info(f"Total Call times: {self.call_times}, Best Found Solution: {self.best_found_clique_size},"
                         f"Current Solution: {objective_value}")
            logging.info(f"Number of constrained variables: {self.added_constraints_size}")

        branching_variable = self.find_branching_variable(solution)

        if branching_variable is None:
            if not check_clique(self.graph, solution)[0]:
                return 0
            self.best_found_clique_size = objective_value
            self.best_solution = solution
        else:
            for branch_value in [1.0, 0.0]:
                self.branch_idx += 1
                current_branch = self.branch_idx
                self.added_constraints_size += 1
                self.add_constraint(branching_variable, branch_value, current_branch)
                self.solve()
                self.delete_constraint(current_branch)
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
