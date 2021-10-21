from time import time
from utils import read_graph, cartesian_product, time_it
import cplex
import numpy as np
import networkx as nx
import logging
from math import floor


class CliqueSolver:
    def __init__(self, graph_path, solve_type, time_limit, debug=False):
        assert solve_type in ["LP", "ILP"], "Solve type should be either LP or ILP"
        self.graph = read_graph(graph_path)
        self.solve_type = solve_type
        self.debug = debug
        self.problem = self.construct_problem()[0]  # time_it returns time additionally
        self.timer = time()
        self.time_limit = time_limit

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
        # num_nodes = graph.vcount()
        num_nodes = self.graph.number_of_nodes()
        obj = [type_one] * num_nodes
        upper_bounds = [type_one] * num_nodes
        lower_bounds = [type_zero] * num_nodes
        types = zip(range(num_nodes), [var_type] * num_nodes)
        # lower bounds are all 0.0 (the default)
        columns_names = [f'x{x}' for x in range(num_nodes)]
        # not_connected = graph.complementer().get_edgelist()
        not_connected = np.array(nx.complement(self.graph).edges)
        # independent_sets = graph.independent_vertex_sets(min=3, max=6)
        independent_sets = self.get_independent_sets()

        problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                              names=columns_names)
        problem.variables.set_types(types)

        constraints = []
        pairs_covered_by_independent_sets = list()
        for ind_set in independent_sets:
            if len(ind_set) > 2:
                constraints.append([[f'x{i}' for i in ind_set], [type_one] * len(ind_set)])
                pairs_covered_by_independent_sets.extend(cartesian_product(ind_set, ind_set))
        if len(pairs_covered_by_independent_sets):
            pairs_covered_by_independent_sets = np.asarray(pairs_covered_by_independent_sets)
            pairs_covered_by_independent_sets = np.unique(np.sort(pairs_covered_by_independent_sets, axis=1), axis=0)  # Edges from nx graph are sorted
            condition = pairs_covered_by_independent_sets[:, 0] == pairs_covered_by_independent_sets[:, 1]
            pairs_covered_by_independent_sets = np.delete(pairs_covered_by_independent_sets, np.where(condition), axis=0)
            not_connected = not_connected[~((not_connected[:, None, :] == pairs_covered_by_independent_sets).all(-1)).any(1)]  # Remove pairs covered by independent sets from not connected
        for xi, xj in not_connected:
            constraints.append(
                [[f'x{xi}', f'x{xj}'], [type_one, type_one]])



        contstraints_length = len(constraints)
        right_hand_side = [type_one] * contstraints_length
        constraint_names = [f'c{x}' for x in range(contstraints_length)]
        constraint_senses = ['L'] * contstraints_length

        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        return problem

    def get_independent_sets(self):
        ind_sets = []
        strategies = [nx.coloring.strategy_largest_first,
                      nx.coloring.strategy_random_sequential,
                      nx.coloring.strategy_independent_set,
                      nx.coloring.strategy_connected_sequential_bfs,
                      nx.coloring.strategy_connected_sequential_dfs,
                      nx.coloring.strategy_saturation_largest_first]

        for strategy in strategies:
            d = nx.coloring.greedy_color(self.graph, strategy=strategy)
            for color in set(color for node, color in d.items()):
                ind_sets.append(
                    [key for key, value in d.items() if value == color])
        return ind_sets

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
    def __init__(self, graph_path, solve_type, time_limit, debug=False):
        super().__init__(graph_path, solve_type, time_limit, debug)
        self.best_found_clique_size = 0
        self.best_solution = None
        self.branch_idx = 0
        self.epsilon = 1e-6
        self.branching_set = set()

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
        # logging.info(self.branching_set)
        self.check_time()
        solution, objective_value = super().solve()
        if floor(objective_value + self.epsilon) <= self.best_found_clique_size:
            return 0

        branching_variable = self.find_branching_variable(solution)

        if branching_variable is None:
            self.best_found_clique_size = objective_value
            self.best_solution = solution
        else:
            self.branch_idx += 1
            # assert branching_variable not in self.branching_set
            # self.branching_set.add(branching_variable)
            current_branch = self.branch_idx
            self.add_constraint(branching_variable, 1.0, current_branch)
            self.solve()
            self.delete_constraint(current_branch)
            self.add_constraint(branching_variable, 0.0, current_branch)
            self.solve()
            self.delete_constraint(current_branch)
            # self.branching_set.remove(branching_variable)
        return 0

    def get_solution(self):
        return self.best_solution

    def get_objective_value(self):
        return self.best_found_clique_size

