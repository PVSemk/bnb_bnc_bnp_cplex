import logging
import time
from argparse import ArgumentParser

import networkx as nx
import numpy as np


def read_graph(path):
    with open(path, "r") as fp:
        for line in fp:
            if line.startswith("p"):
                _, name, vertices_num, edges_num = line.split()
                adjacency_matrix = np.zeros(
                    (int(vertices_num), (int(vertices_num))), dtype=np.bool,
                )
            elif line.startswith("e"):
                _, v1, v2 = line.split()
                adjacency_matrix[int(v1) - 1, int(v2) - 1] = 1
            else:
                continue
    # np.fill_diagonal(adjacency_matrix, 1)
    graph = nx.convert_matrix.from_numpy_matrix(adjacency_matrix)
    return graph


def cartesian_product(x, y):
    return np.dstack(np.meshgrid(x, y)).reshape(-1, 2)


def parse_args():
    parser = ArgumentParser(description="Finds max clique for DIMACS graphs")
    parser.add_argument(
        "-p",
        "--path",
        help="Path to source graph file in .clq format or graph list in .txt format (see README.md for details) ",
        default="input.txt",
        type=str,
    )

    parser.add_argument(
        "-uh",
        "--use_heuristics",
        action="store_true",
        help="Use heuristics (ILS-based) to generate an initial solution",
    )
    parser.add_argument(
        "-t",
        "--time_limit",
        type=int,
        default=3600,
        help="Time limit for processing the graph (in secs)",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Allow debug prints from cplex",
    )

    return parser.parse_args()


def time_it(func):
    """
    Measures time
    """

    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = func(*args, **kwargs)
        time2 = time.time()
        final_time = time2 - time1
        mins, secs = divmod(final_time, 60)
        logging.info(f"{func.__name__} function took {mins} mins, {secs:.2f} secs")
        return ret, final_time * 1000

    return wrap


def check_clique(graph, solution, best_known_solution_size=None):
    solution = np.array(solution)
    clique_nodes = np.where(np.isclose(solution, 1.0, atol=1e-4))[0]
    clique_candidate = graph.subgraph(clique_nodes)
    num_nodes = len(clique_nodes)
    size_match = (
        len(clique_nodes) == best_known_solution_size
        if best_known_solution_size
        else None
    )

    return clique_candidate.size() == num_nodes * (num_nodes - 1) / 2, size_match
