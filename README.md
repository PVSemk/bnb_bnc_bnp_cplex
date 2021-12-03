# Max Clique problem

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

| Graph                     |   Found Answer    |  Best Known Answer   | BnC Time (sec) 	 |   Total Time (sec)   |  Reached Time Limit 	  | Difficult 	 | Notes                                                                                                                    	 |
|:--------------------------|:-----------------:|:--------------------:|:----------------:|:--------------------:|:----------------------:|-------------|:--------------------------------------------------------------------------------------------------------------------------:|
| johnson8-2-4.clq          | 4               	 |          4           | 0.00           	 |  0.048            	  |         False          | E         	 |                                                             	                                                              |
| johnson8-4-4.clq          | 14              	 | 14                 	 | 0.00           	 |  0.10             	  | False                	 | E         	 |                                                             	                                                              |
| johnson16-2-4.clq         |   8           	   |  8                	  | 0.00           	 |  0.226            	  |  False              	  | E         	 |                                                             	                                                              |
| MANN_a9.clq               | 16              	 | 16                	  | 0.12          	  |  0.198            	  |  False              	  | E         	 |                                                             	                                                              |
| keller4.clq               |        11         |          11          |       198        |        199.3         |         False          | E           |                                                                                                                            |
| hamming6-2.clq            | 32              	 | 32                	  | 0.00           	 | 0.182             	  |  False              	  | E         	 |                                                             	                                                              |
| hamming6-4.clq         	  |         4         |  4                	  | 0.85          	  |  0.901            	  |  False              	  | E         	 |                                                             	                                                              |
| hamming8-2.clq     	      | 128            	  | 128                	 | 0.01           	 |  5.9             	   | False               	  | E         	 |                                                                                                                            |
| hamming8-4.clq     	      |  16            	  | 16                	  |  0.7          	  |  1.839           	   |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-1.clq     	      |        12         | 12                	  |  0.02         	  | 0.33              	  |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-2.clq     	      |        24         | 24                	  |  0.01         	  |  0.447            	  |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-5.clq            |        58         | 58                	  |  4.99         	  |   6.15           	   |  False              	  | E         	 |                                                                                                                            |
| c-fat500-1.clq            |  14           	   | 14                	  | 0.02           	 |  1.71             	  |  False              	  | E         	 |                                                             	                                                              |
| c-fat500-10.clq           |  126           	  | 126                	 |       0.22       | 10.57             	  | False               	  | E         	 |                                                             	                                                              |
| c-fat500-2.clq            |  26           	   | 26                	  | 0.04           	 |  2.46             	  | False               	  | E         	 |                                                             	                                                              |
| c-fat500-5.clq  	         |        64         | 64                	  |       0.15       |  4.93             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.7_1.clq        	 |        30         | 30                	  |       0.32       |        1.196         | False               	  | E         	 |                                                             	                                                              |
| san200_0.7_2.clq          |  18           	   | 18                	  |      39.86       |  40.6             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.9_1.clq          |  70           	   | 70                	  |       0.07       |  1.89             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.9_2.clq          |  60           	   | 60                	  |       0.05       |  1.61             	  | False               	  | E         	 |                                                             	                                                              |
| C125.9.clq                |  34           	   | 34                	  |       644        | 645.40             	 | False               	  | M	          |                                                             	                                                              |
| brock200_1.clq            |  21           	   | 21                	  |       3600       |  3600             	  |  True               	  | M         	 |                                                             	                                                              |
| brock200_2.clq            |  12           	   | 12                	  |       1088       |  1088             	  | False               	  | M         	 |                                                             	                                                              |
| brock200_3.clq            |  15           	   | 15                	  |       2035       |  2035             	  | False               	  | M         	 |                                                             	                                                              |
| brock200_4.clq            |  17           	   | 17                	  |       2176       |  2176             	  | False               	  | M         	 |                                                             	                                                              |
| gen200_p0.9_44.clq        |  39           	   | 44                	  |       3600       |  3600             	  |  True               	  | M         	 |                                                             	                                                              |
| gen200_p0.9_55.clq        |  55           	   | 55                	  |       2.33       |  3.85             	  | False               	  | M         	 |                                                             	                                                              |
| p_hat300-1.clq            |         8         |          8           |       1404       |         1405         |         False          | M           |                                                                                                                            |
| p_hat300-2.clq            |        25         |          25          |       1914       |         1916         |         False          | M           |                                                                                                                            |
| san200_0.9_3.clq          |        37         |          44          |       3600       |         3600         |          True          | M           |                                                                                                                            |
| MANN_a27.clq              |        126        |         126          |       184        |         202          |         False          | H           |                                                                                                                            |
| MANN_a45.clq              |        345        |         345          |       3600       |         3600         |          True          | H           |                                                                                                                            |
| p_hat300-3.clq            |        34         |          36          |       3600       |         3600         |          True          | H           |                                                                                                                            |
| sanr200_0.7.clq           |        18         |          18          |       3600       |         3600         |          True          | H           |                                                                                                                            |

## Installation & Usage
1. Install IBM CPLEX, setup it for Python
2. Launch `pip install -r requirements.txt`
3. Run `python main.py -p path/to/input/file`. Usage example:
```
usage: main.py [-h] [-p PATH] [-uh] [-t TIME_LIMIT] [-d]

Finds max clique for DIMACS graphs

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to source graph file in .clq format or graph list
                        in .txt format (see README.md for details)
  -uh, --use_heuristics
                        Use heuristics (ILS-based) to generate an initial
                        solution
  -t TIME_LIMIT, --time_limit TIME_LIMIT
                        Time limit for processing the graph (in secs)
  -d, --debug           Allow debug prints from cplex


```
- We support either single processing (file should have *.clq* extension) or multiple processing (*.txt* extension)
- This repository contains both naive cplex and BnB algorithm, but currently `main.py` supports BnC only
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
