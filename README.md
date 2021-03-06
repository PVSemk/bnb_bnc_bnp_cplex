# Max Clique problem
## Repository Overview
This repository contains implementation of BnB, BnC algorithms (with cplex solver) for Max Clique problem and BnP algorithm for Vertex Coloring problem

Implementations can be found in following branches:
1. [BnB](https://github.com/PVSemk/max_clique_cplex/tree/main)
2. [BnC](https://github.com/PVSemk/max_clique_cplex/tree/ps/BnC)
3. [BnP](https://github.com/PVSemk/max_clique_cplex/tree/ps/BnP)

## Machine configuration
```
AMD Ryzen 7 3700X 8-Core Processor @ 3.60 Ghz
64 GB RAM
```

## Achieved results
Benchmark - subset from DIMACS
Time Limit was set to 1 hour (3600 secs) for easy/medium and 2 hours (7200 secs) for hard/timeout_medium.

For hard/timeout_medium `n_independent_sets_growth_ratio` was set to 0.01

Achieved results (E - easy, M - middle, H - hard):

| Graph              	| Found Answer 	| Best Known Answer 	| BnB Time (sec) 	| Total Time (sec) 	| Reached Time Limit 	| Difficult 	| Notes                                                                                                                    	|
|--------------------	|--------------	|-------------------	|----------------	|------------------	|--------------------	|-----------	|--------------------------------------------------------------------------------------------------------------------------	|
| johnson8-2-4.clq   	| 4            	| 4                 	| 0.00           	| 0.148            	| False              	| E         	|                                                                                                                          	|
| johnson16-2-4.clq  	| 8            	| 8                 	| 0.00           	| 4.21             	| False              	| E         	|                                                                                                                          	|
| MANN_a9.clq        	| 16           	| 16                	| 0.03           	| 0.118            	| False              	| E         	|                                                                                                                          	|
| keller4.clq        	| 11           	| 11                	| 53.39          	| 66.56            	| False              	| E         	|                                                                                                                          	|
| hamming8-4.clq     	| 16           	| 16                	| 1.05           	| 35.9             	| False              	| E         	|                                                                                                                          	|
| C125.9.clq         	| 34           	| 34                	| 265.7          	| 268.9            	| False              	| M         	|                                                                                                                          	|
| brock200_1.clq     	| 21           	| 21                	| 2933           	| 2982             	| False               	| M         	| n_independent_sets_growth_ratio was set to 0.01 (default is 0.02) to generate more independent sets (see logs)            |
| brock200_2.clq     	| 12           	| 12                	| 88.89          	| 108.73           	| False              	| M         	|                                                                                                                          	|
| brock200_3.clq     	| 15           	| 15                	| 437.19         	| 459              	| False              	| M         	|                                                                                                                          	|
| brock200_4.clq     	| 17           	| 17                	| 565.44         	| 588.3            	| False              	| M         	|                                                                                                                          	|
| gen200_p0.9_44.clq 	| 44           	| 44                	| 288.14         	| 323.26           	| False              	| M         	| Hard-coded number of independent set searching iterations to 50 as with default strategy it's out of time limit (see logs)|
| gen200_p0.9_55.clq 	| 55           	| 55                	| 0.43           	| 19.9             	| False              	| M         	|                                                                                                                          	|
| p_hat1000-1.clq    	| 10           	| 10                	| 7200           	| 7200             	| True               	| M         	|                                                                                                                          	|
| san1000.clq        	| 10           	| 15                	| 7200           	| 7200             	| True               	| M         	|                                                                                                                          	|
| MANN_a27.clq        	| 126           | 126                	| 21.41           	| 42             	| False               	| H         	|                                                                                                                          	|
| MANN_a45.clq        	| 345           | 345                	| 924.82           	| 1167              | False               	| H         	|                                                                                                                          	|
| brock400_1.clq        | 23           	| 27                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| brock400_2.clq        | 24           	| 29                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| brock400_3.clq        | 23           	| 31                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| brock400_4.clq        | 24           	| 33                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| p_hat300-3.clq        | 36           	| 36                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| p_hat500-3.clq        | 49           	| 50                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| p_hat1000-2.clq       | 45           	| 46                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| p_hat1500-1.clq       | 10           	| 12                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| sanr200_0.9.clq       | 42           	| 42                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|
| sanr400_0.7.clq       | 21           	| 21                	| 7200           	| 7200             	| True               	| H         	|                                                                                                                          	|

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
