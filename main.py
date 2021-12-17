import json
import logging
import os
import sys
from datetime import datetime

from bnp_max_clique import BnPColoringSolver
from utils import parse_args, read_graph, time_it


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
    solver = BnPColoringSolver(graph, args.time_limit, debug=args.debug)
    time_limit_reached = False
    try:
        solver()
    except (TimeoutError, KeyboardInterrupt):
        logging.error("Out of time!")
        time_limit_reached = True
    except Exception as msg:
        logging.error(msg)
        raise msg
    finally:
        solution_values = solver.get_solution()
        objective_value = solver.get_objective_value()
        print_solution(solution_values, objective_value)
    return objective_value, time_limit_reached  # noqa:B012


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
        for (path, best_known_size) in inputs:
            filename = os.path.basename(path)
            logging.info(f"\n\nPROCESSING: {os.path.basename(path)}")
            graph_results = {}
            (
                (found_clique_size, time_limit_reached),
                processing_time,
            ) = process_single_graph(
                path, args, best_known_solution=int(best_known_size),
            )
            graph_results["Time (msec.)"] = processing_time
            graph_results["Time (sec.)"] = processing_time / 1000
            graph_results["Found Answer"] = found_clique_size
            graph_results["Best Known Answer"] = best_known_size
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
