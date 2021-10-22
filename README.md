# Max Clique problem

## Machine configuration
```
AMD Ryzen 7 3700X 8-Core Processor @ 3.60 Ghz
64 GB RAM
```

## Achieved results
Benchmark - subset from DIMACS

Achieved results (E - easy, M - middle, H - hard):

## Installation & Usage
1. Install IBM CPLEX, setup it for Python
2. Launch `pip install -r requirements.txt`
3. Run `python main.py -p path/to/input/file`. Usage example:
```
usage: main.py [-h] [-p PATH] [-m {LP,ILP}] [-uh] [-t TIME_LIMIT] [-d]

Finds max clique for DIMACS graphs

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to source graph file in .clq format or graph list
                        in .txt format (see README.md for details)
  -m {LP,ILP}, --method {LP,ILP}
                        Treat the problem as LP or ILP
  -uh, --use_heuristics
                        Use heuristics (ILS-based) to generate an initial
                        solution
  -t TIME_LIMIT, --time_limit TIME_LIMIT
                        Time limit for processing the graph (in secs)
  -d, --debug           Allow debug prints from cplex


```
- We support either single processing (file should have *.clq* extension) or multiple processing (*.txt* extension)
- This repository contains both naive cplex and BnB algorithm, but currently `main.py` supports BnB only, so you should use `--method LP` (default) only
- Implemented heuristics:
  - Greedy Search with the largest degrees first + Randomized Version
  - Greedy Search with the smallest degree last with removal + Randomized version
  - The initial solution is the best from all heuristics
### Multiple input structure
  We expect `.txt` file with the following structure:
```
File,Answer,Level
graph.clq,8,E
...
```
## Sample Output
```
PROCESSING: johnson8-2-4.clq
2021-10-22 23:38:51,270 [INFO] Searched for independent sets during 3 iterations
2021-10-22 23:38:51,274 [INFO] construct_problem function took 0.0 mins, 0.02 secs
2021-10-22 23:38:51,274 [INFO] Using heuristics
2021-10-22 23:38:51,280 [INFO] Finished with heuristics, found solution length: 4, it's a clique: True
2021-10-22 23:38:51,283 [INFO] __call__ function took 0.0 mins, 0.00 secs
2021-10-22 23:38:51,283 [INFO] objective value: 4
2021-10-22 23:38:51,283 [INFO] values:
2021-10-22 23:38:51,283 [INFO] 	x_0 = 1.0 	x_5 = 1.0 	x_14 = 1.0 	x_27 = 1.0
2021-10-22 23:38:51,284 [INFO] Found nodes create a clique
2021-10-22 23:38:51,284 [INFO] It's size matches with the best known
2021-10-22 23:38:51,284 [INFO] process_single_graph function took 0.0 mins, 0.03 secs
```
Results (for multiple processing) and logs will be stored in `results/` and `logs/` folders correspondingly
## Developing
1. Run `pip install -r requirements-dev.txt`
2. Setup pre-commit with `pre-commit install
