from utils import parse_args, time_it
from bnb_max_clique import BnBCliqueSolver
import numpy as np
import logging
import json
import os
from datetime import datetime
import sys


def print_solution(solution_values, objective_value):
    logging.info(f"objective value: {objective_value} ")
    logging.info("values:")
    logging_str = ""
    for idx in range(len(solution_values)):
        if solution_values[idx] != 0:
            logging_str += f"\tx_{idx} = {solution_values[idx]} "
    logging.info(logging_str)


def check_clique(graph, solution, best_known_solution_size=None):
    solution = np.array(solution)
    clique_nodes = np.where(np.isclose(solution, 1.0, atol=1e-4))[0]
    clique_candidate = graph.subgraph(clique_nodes)
    num_nodes = len(clique_nodes)
    size_match = len(clique_nodes) == best_known_solution_size if best_known_solution_size else None

    return clique_candidate.size() == num_nodes * (num_nodes - 1) / 2, size_match


@time_it
def process_single_graph(path, method, time_limit, debug=False, best_known_solution=None):
    logging.info(f"\n\nPROCESSING: {os.path.basename(path)}")
    solver = BnBCliqueSolver(path, method, time_limit, debug=debug)
    time_limit_reached = False
    try:
        solver()
    except (TimeoutError, KeyboardInterrupt):
        logging.warning("Out of time!")
        time_limit_reached = True
    finally:
        solution_values = solver.get_solution()
        objective_value = solver.get_objective_value()
        print_solution(solution_values, objective_value)
        is_clique, size_match_with_best_known = check_clique(solver.graph, solution_values, best_known_solution)
        if is_clique:
            logging.info("Found nodes create a clique")
            if size_match_with_best_known:
                logging.info("It's size matches with the best known")
        else:
            logging.warning("Found nodes don't form a clique!")
        return objective_value, is_clique, time_limit_reached


@time_it
def main():
    args = parse_args()
    start_time_formatted = datetime.now().strftime('%d-%m-%Y_%H-%M-%S.log')
    os.makedirs("logs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        handlers=[
                            logging.FileHandler(f"logs/{start_time_formatted}"),
                            logging.StreamHandler(sys.stdout)
                        ])
    logging.info(f"Time Limit: {args.time} secs")
    if ".txt" in args.path:
        total_results = {}
        with open(args.path, "r") as fp:
            inputs = [line.rstrip().split(",") for line in fp.readlines()[1:]]
        for (path, best_known_size, difficult_level) in inputs:
            filename = os.path.basename(path)
            graph_results = {}
            (found_clique_size, is_clique, time_limit_reached), processing_time = process_single_graph(path, args.method, args.time, args.debug, int(best_known_size))
            graph_results["Time (msec.)"] = processing_time
            graph_results["Time (sec.)"] = processing_time / 1000
            graph_results["Found Answer"] = found_clique_size
            graph_results["Best Known Answer"] = best_known_size
            graph_results["Type"] = difficult_level
            graph_results["Reached Time Limit"] = time_limit_reached
            total_results[filename] = graph_results
        with open(f"outputs/{start_time_formatted}", "w") as fp:
            json.dump(total_results, fp, indent=4, sort_keys=False)
    else:
        process_single_graph(args.path, args.method, args.time, args.debug)


if __name__ == "__main__":
    main()
