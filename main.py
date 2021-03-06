import json
import logging
import os
import sys
from datetime import datetime

from bnb_max_clique import BnBCliqueSolver
from heuristic import GreedyHeuristic
from utils import check_clique, parse_args, read_graph, time_it


def print_solution(solution_values, objective_value):
    logging.info(f"objective value: {objective_value} ")
    logging.info("values:")
    logging_str = ""
    for idx in range(len(solution_values)):
        if solution_values[idx] != 0:
            logging_str += f"\tx_{idx} = {solution_values[idx]} "
    logging.info(logging_str)


@time_it
def process_single_graph(path, args, best_known_solution=None):
    graph = read_graph(path)
    solver = BnBCliqueSolver(graph, args.method, args.time_limit, debug=args.debug)
    if args.use_heuristics:
        logging.info("Using heuristics")
        heuristic_solver = GreedyHeuristic(graph)
        heuristic_solution, heuristic_objective_value = heuristic_solver()
        is_clique = check_clique(graph, heuristic_solution)[0]
        logging.info(
            f"Finished with heuristics, found solution length: {heuristic_objective_value}, it's a clique: {is_clique}",
        )
        if is_clique:
            solver.set_objective_value(heuristic_objective_value)
            solver.set_solution(heuristic_solution)
    time_limit_reached = False
    try:
        solver()
    except (TimeoutError, KeyboardInterrupt):
        logging.warning("Out of time!")
        time_limit_reached = True
    except Exception as msg:
        logging.warning(msg)
    finally:
        solution_values = solver.get_solution()
        objective_value = solver.get_objective_value()
        print_solution(solution_values, objective_value)
        is_clique, size_match_with_best_known = check_clique(
            solver.graph, solution_values, best_known_solution,
        )
        if is_clique:
            logging.info("Found nodes create a clique")
            if size_match_with_best_known:
                logging.info("It's size matches with the best known")
        else:
            logging.warning("Found nodes don't form a clique!")
        return objective_value, is_clique, time_limit_reached  # noqa:B012


@time_it
def main():
    args = parse_args()
    start_time_formatted = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    os.makedirs("logs", exist_ok=True)
    os.makedirs(os.path.join("outputs", start_time_formatted), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO if not args.debug else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"logs/{start_time_formatted}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.info(f"Time Limit: {args.time_limit} secs")
    if ".txt" in args.path:
        with open(args.path, "r") as fp:
            inputs = [line.rstrip().split(",") for line in fp.readlines()[1:]]
        for (path, best_known_size, difficult_level) in inputs:
            filename = os.path.basename(path)
            logging.info(f"\n\nPROCESSING: {os.path.basename(path)}")
            graph_results = {}
            (
                (found_clique_size, is_clique, time_limit_reached),
                processing_time,
            ) = process_single_graph(
                path, args, best_known_solution=int(best_known_size),
            )
            graph_results["Time (msec.)"] = processing_time
            graph_results["Time (sec.)"] = processing_time / 1000
            graph_results["Found Answer"] = found_clique_size
            graph_results["Best Known Answer"] = best_known_size
            graph_results["Type"] = difficult_level
            graph_results["Reached Time Limit"] = time_limit_reached
            with open(
                os.path.join("outputs", start_time_formatted, f"{filename}.json"), "w",
            ) as fp:
                json.dump(graph_results, fp, indent=4, sort_keys=False)
    else:
        filename = os.path.basename(args.path)
        graph_results = {}
        (
            (found_clique_size, is_clique, time_limit_reached),
            processing_time,
        ) = process_single_graph(args.path, args)
        graph_results["Time (msec.)"] = processing_time
        graph_results["Time (sec.)"] = processing_time / 1000
        graph_results["Found Answer"] = found_clique_size
        graph_results["Reached Time Limit"] = time_limit_reached
        with open(
            os.path.join("outputs", start_time_formatted, f"{filename}.json"), "w",
        ) as fp:
            json.dump(graph_results, fp, indent=4, sort_keys=False)


if __name__ == "__main__":
    main()
