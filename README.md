# Max Clique problem

## Machine configuration
```
AMD Ryzen 7 3700X 8-Core Processor @ 3.60 Ghz
64 GB RAM
```

## Achieved results
Benchmark - subset from DIMACS
Time Limit was set to 2 hours (7200 sec).

Achieved results (E - easy, M - middle, H - hard):

| Graph                     |   Found Answer    |  Best Known Answer   |  Total Time (sec)   |  Reached Time Limit 	  | Difficult 	 | Notes                                                                                                                    	 |
|:--------------------------|:-----------------:|:--------------------:|:-------------------:|:----------------------:|-------------|:--------------------------------------------------------------------------------------------------------------------------:|
| johnson8-2-4.clq          | 4               	 |          4           |  0.04            	  |         False          | E         	 |                                                             	                                                              |
| johnson8-4-4.clq          | 14              	 | 14                 	 | 0.15             	  | False                	 | E         	 |                                                             	                                                              |
| johnson16-2-4.clq         |   8           	   |  8                	  |  0.32            	  |  False              	  | E         	 |                                                             	                                                              |
| MANN_a9.clq               | 16              	 | 16                	  |  0.18            	  |  False              	  | E         	 |                                                             	                                                              |
| keller4.clq               |        11         |          11          |        92.9         |         False          | E           |                                                                                                                            |
| hamming6-2.clq            | 32              	 | 32                	  | 0.169             	 |  False              	  | E         	 |                                                             	                                                              |
| hamming6-4.clq         	  |         4         |  4                	  |  0.40            	  |  False              	  | E         	 |                                                             	                                                              |
| hamming8-2.clq     	      | 128            	  | 128                	 | 5.45             	  | False               	  | E         	 |                                                                                                                            |
| hamming8-4.clq     	      |  16            	  | 16                	  |  1.10           	   |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-1.clq     	      |        12         | 12                	  | 0.32              	 |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-2.clq     	      |        24         | 24                	  |  0.44            	  |  False              	  | E         	 |                                                             	                                                              |
| c-fat200-5.clq            |        58         | 58                	  |  2.77           	   |  False              	  | E         	 |                                                                                                                            |
| c-fat500-1.clq            |  14           	   | 14                	  | 1.66             	  |  False              	  | E         	 |                                                             	                                                              |
| c-fat500-10.clq           |  126           	  | 126                	 | 9.36             	  | False               	  | E         	 |                                                             	                                                              |
| c-fat500-2.clq            |  26           	   | 26                	  | 2.37             	  | False               	  | E         	 |                                                             	                                                              |
| c-fat500-5.clq  	         |        64         | 64                	  | 4.58             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.7_1.clq        	 |        30         | 30                	  |        0.88         | False               	  | E         	 |                                                             	                                                              |
| san200_0.7_2.clq          |  18           	   | 18                	  | 12.2             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.9_1.clq          |  70           	   | 70                	  | 1.72             	  | False               	  | E         	 |                                                             	                                                              |
| san200_0.9_2.clq          |  60           	   | 60                	  | 1.48             	  | False               	  | E         	 |                                                             	                                                              |
| C125.9.clq                |  34           	   | 34                	  |  266             	  | False               	  | M	          |                                                             	                                                              |
| brock200_1.clq            |  21           	   | 21                	  | 3463             	  | False               	  | M         	 |                                                             	                                                              |
| brock200_2.clq            |  12           	   | 12                	  |  604             	  | False               	  | M         	 |                                                             	                                                              |
| brock200_3.clq            |  15           	   | 15                	  | 1067             	  | False               	  | M         	 |                                                             	                                                              |
| brock200_4.clq            |  17           	   | 17                	  | 1121             	  | False               	  | M         	 |                                                             	                                                              |
| gen200_p0.9_44.clq        |  39           	   | 44                	  | 7200             	  |  True               	  | M         	 |                                                             	                                                              |
| gen200_p0.9_55.clq        |  55           	   | 55                	  |  36             	   | False               	  | M         	 |                                                             	                                                              |
| p_hat300-1.clq            |         8         |          8           |         989         |         False          | M           |                                                                                                                            |
| p_hat300-2.clq            |        25         |          25          |        1212         |         False          | M           |                                                                                                                            |
| san200_0.9_3.clq          |        37         |          44          |        7200         |          True          | M           |                                                                                                                            |
| MANN_a27.clq              |        126        |         126          |         66          |         False          | H           |                                                                                                                            |
| MANN_a45.clq              |        345        |         345          |        2340         |         False          | H           |                                                                                                                            |
| p_hat300-3.clq            |        35         |          36          |        7200         |          True          | H           |                                                                                                                            |
| sanr200_0.7.clq           |        18         |          18          |        1916         |         False          | H           |                                                                                                                            |

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
