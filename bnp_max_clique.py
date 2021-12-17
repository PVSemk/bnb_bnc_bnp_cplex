import logging
from math import ceil
from time import time

import cplex
import networkx as nx
import networkx.algorithms.mis
import numpy as np

from heuristic_algorithms import ColoringHeuristic, ViolatedContraintsHeuristic
from utils import time_it


class ColoringSolver:
    def __init__(self, graph, time_limit, debug=False):
        self.graph = graph
        self.debug = debug
        self.timer = time()
        self.time_limit = time_limit
        self.variables = None
        self.problem = self.construct_problem()[0]  # time_it returns time additionally
        self.complement_graph = nx.complement(self.graph)

    @time_it
    def construct_problem(self):
        problem = cplex.Cplex()
        if not self.debug:
            problem.set_log_stream(None)
            problem.set_results_stream(None)
            problem.set_warning_stream(None)
            problem.set_error_stream(None)

        problem.objective.set_sense(problem.objective.sense.minimize)
        coloring_heuristic = ColoringHeuristic(self.graph, growth_ratio=0.05)
        type_one = 1.0
        # var_type = problem.variables.type.continuous
        self.variables = coloring_heuristic()
        n_variables = len(self.variables)
        obj = [type_one] * n_variables
        # types = zip(range(n_variables), [var_type] * n_variables)
        columns_names = [f"x{x}" for x in range(n_variables)]

        problem.variables.add(
            obj=obj, names=columns_names,
        )
        # problem.variables.set_types(types)

        constraints = []
        for node in range(self.graph.number_of_nodes()):
            contraint = [
                f"x{i}" for i in range(n_variables) if node in self.variables[i]
            ]
            constraints.append([contraint, [type_one] * len(contraint)])

        contstraints_length = len(constraints)
        right_hand_side = [type_one] * contstraints_length
        constraint_names = [f"n{i}" for i in range(contstraints_length)]
        constraint_senses = ["G"] * contstraints_length

        problem.linear_constraints.add(
            lin_expr=constraints,
            senses=constraint_senses,
            rhs=right_hand_side,
            names=constraint_names,
        )
        return problem

    def solve(self):
        self.problem.solve()
        solution = self.problem.solution.get_values()
        dual_solution = self.problem.solution.get_dual_values()
        objective_value = self.problem.solution.get_objective_value()
        return solution, objective_value, dual_solution

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


class BnPSlaveProblemCplex:
    def __init__(self, graph):
        self.graph = graph
        self.coloring_heuristic = ColoringHeuristic(
            self.graph, growth_ratio=0.02, log=False,
        )
        self.problem = None
        self.type_one = 1

    def construct_slave_problem(self, obj, forbidden_sets, time_limit=None):
        if self.problem is None:
            problem = cplex.Cplex()
            problem.set_problem_type(problem.problem_type.MILP)
            if time_limit is not None:
                problem.parameters.timelimit.set(time_limit)
            problem.set_log_stream(None)
            problem.set_results_stream(None)
            problem.set_warning_stream(None)
            problem.set_error_stream(None)
            problem.objective.set_sense(problem.objective.sense.maximize)
            var_type = problem.variables.type.binary
            n_variables = len(obj)
            types = zip(range(n_variables), [var_type] * n_variables)
            columns_names = [f"y{i}" for i in range(n_variables)]

            problem.variables.add(
                obj=obj, names=columns_names,
            )
            problem.variables.set_types(types)

            constraints = []
            cliques = self.coloring_heuristic()
            for clique in cliques:
                if clique in forbidden_sets or len(clique) < 3:
                    continue
                constraints.append(
                    [[f"y{i}" for i in clique], [self.type_one] * len(clique)],
                )
            connected = np.array(nx.complement(self.graph).edges)
            for xi, xj in connected:
                constraints.append(
                    [[f"y{xi}", f"y{xj}"], [self.type_one, self.type_one]],
                )
            right_hand_side = [self.type_one] * len(constraints)
            constraint_names = [f"c{i}" for i in range(len(constraints))]
            for forbidden_set in forbidden_sets:
                constraints.append(
                    [
                        [f"y{i}" for i in forbidden_set],
                        [self.type_one] * len(forbidden_set),
                    ],
                )
                right_hand_side.append(len(forbidden_set) - 1)
                constraint_names.append(f"f{len(constraints)}")

            constraint_senses = ["L"] * len(constraints)

            problem.linear_constraints.add(
                lin_expr=constraints,
                senses=constraint_senses,
                rhs=right_hand_side,
                names=constraint_names,
            )
            self.problem = problem
        else:
            if time_limit is None:
                self.problem.parameters.timelimit.reset()
            else:
                self.problem.parameters.timelimit.set(time_limit)
            self.problem.objective.set_linear(zip(range(len(obj)), obj))
            for constraint_name in self.problem.linear_constraints.get_names():
                if "f" in constraint_name:
                    self.problem.linear_constraints.delete(constraint_name)
            constraints = []
            right_hand_side = []
            constraint_names = []
            for i, forbidden_set in enumerate(forbidden_sets):
                constraints.append(
                    [
                        [f"y{i}" for i in forbidden_set],
                        [self.type_one] * len(forbidden_set),
                    ],
                )
                right_hand_side.append(len(forbidden_set) - 1)
                constraint_names.append(f"f{i}")
            self.problem.linear_constraints.add(
                lin_expr=constraints,
                senses=["L"] * len(constraints),
                rhs=right_hand_side,
                names=constraint_names,
            )

    def solve(self):
        self.problem.solve()
        solution = self.problem.solution.get_values()
        objective_value = self.problem.solution.MIP.get_best_objective()
        if objective_value > 1.0 + 1e-6:
            return [tuple(np.where(np.isclose(solution, 1))[0])], objective_value
        else:
            return None, objective_value


class BnPColoringSolver(ColoringSolver):
    def __init__(self, graph, time_limit, debug=False):
        super().__init__(graph, time_limit, debug)
        self.branch_idx = 0
        self.epsilon = 1e-6
        self.call_times = 0
        self.violated_constraints_heuristic = ViolatedContraintsHeuristic(
            self.complement_graph,
        )
        self.variables_searching_limit = 10
        self.forbidden_sets = []
        self.slave_problem = BnPSlaveProblemCplex(self.complement_graph)
        self.best_found_colors_number = None
        self.best_solution = None

    def add_branching_constraint(self, variable, rhs, branch_idx):
        self.problem.linear_constraints.add(
            lin_expr=[[[f"x{variable}"], [1.0 if rhs == 1.0 else -1.0]]],
            senses=["G"],
            rhs=[rhs],
            names=[f"branch_{branch_idx}"],
        )

    def add_violated_constraint_as_variable(self, independent_set):
        self.variables.append(independent_set)
        variable_idx = self.problem.variables.get_num()
        name = [f"x{variable_idx}"]
        obj = [1.0]
        self.problem.variables.add(
            obj=obj, names=name,
        )
        for node in independent_set:
            existing_constraint = self.problem.linear_constraints.get_rows(f"n{node}")
            existing_constraint.ind.append(variable_idx)
            existing_constraint.val.append(1.0)
            self.problem.linear_constraints.set_linear_components(
                f"n{node}", existing_constraint,
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

    def column_generation_loop(
        self, dual_solution, objective_value, use_cplex=False, time_limit=None,
    ):  # ToDo: time_limit - object to tune
        while True:
            dual_solution = dual_solution[: self.graph.number_of_nodes()]
            if use_cplex:
                self.slave_problem.construct_slave_problem(
                    dual_solution, self.forbidden_sets, time_limit=time_limit,
                )
                violated_contraints, upper_bound = self.slave_problem.solve()

            else:
                violated_contraints, upper_bound = self.violated_constraints_heuristic(
                    dual_solution,
                )
            if upper_bound is not None:
                lower_bound = ceil(objective_value / upper_bound)
                if (
                    self.best_found_colors_number is not None
                    and lower_bound >= self.best_found_colors_number
                ):
                    return True, None, None, None
            if violated_contraints is None:
                solution = self.problem.solution.get_values()
                break
            for violated_constraint in violated_contraints:
                if violated_constraint not in self.forbidden_sets:
                    self.add_violated_constraint_as_variable(violated_constraint)
            solution, objective_value, dual_solution = self.call_solver()
        return False, solution, objective_value, dual_solution

    def call_solver(self):
        try:
            solution, objective_value, dual_solution = super().solve()
        except cplex.exceptions.CplexSolverError as msg:
            logging.warning(f"CPLEX Error: {msg}")
            return None, None, None
        return solution, objective_value, dual_solution

    def solve(self):
        self.call_times += 1
        self.check_time()
        solution, objective_value, dual_solution = self.call_solver()
        for use_cplex in [False, True]:
            (
                can_prune_branch,
                solution,
                objective_value,
                dual_solution,
            ) = self.column_generation_loop(
                dual_solution, objective_value, use_cplex=use_cplex, time_limit=2,
            )
            if can_prune_branch:
                print("Pruned")
                return 0
        branching_variable = self.find_branching_variable(solution)
        if branching_variable is None:
            (
                can_prune_branch,
                solution,
                objective_value,
                dual_solution,
            ) = self.column_generation_loop(
                dual_solution,
                objective_value,
                use_cplex=True,
                time_limit=self.time_limit,
            )
            if can_prune_branch:
                print("Pruned")
                return 0
            branching_variable = self.find_branching_variable(solution)
            if branching_variable is None:
                if (
                    self.best_found_colors_number is None
                    or ceil(objective_value - self.epsilon)
                    < self.best_found_colors_number
                ):
                    self.best_solution = solution
                    self.best_found_colors_number = objective_value
                return 0

        if self.call_times % 10 == 0:
            logging.info(
                f"Total Call times: {self.call_times}, Best Found Solution: {self.best_found_colors_number},"
                f"Current Solution: {objective_value}",
            )
        # ToDo: Доделать
        for branch_value in [1.0, 0.0]:
            self.branch_idx += 1
            current_branch = self.branch_idx
            self.add_branching_constraint(
                branching_variable, branch_value, current_branch,
            )
            if branch_value == 0.0:
                self.forbidden_sets.append(self.variables[branching_variable])
            self.solve()
            self.delete_branching_constraint(current_branch)
            if branch_value == 0.0:
                self.forbidden_sets.pop()
        return 0

    def get_solution(self):
        return self.best_solution

    def get_objective_value(self):
        return self.best_found_colors_number

    def set_objective_value(self, objective_value):
        self.best_found_colors_number = objective_value

    def set_solution(self, solution):
        self.best_solution = solution
