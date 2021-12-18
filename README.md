# Vertex Coloring problem with BnP algorithm

## Machine configuration
```
AMD Ryzen 7 3700X 8-Core Processor @ 3.60 Ghz
64 GB RAM
```

## Achieved results
Time Limit was set to 2 hours (7200 sec).

Achieved results (E - easy, M - middle, H - hard):

| Graph              | Best Known Answer |    Found Answer     |  Total Time (sec)  |  Reached Time Limit 	  |
|:-------------------|:-----------------:|:-------------------:|:------------------:|:----------------------:|
| myciel3            | 4               	 |          4          | 0.15            	  |         False          |
| myciel4            | 5              	  | 5                 	 |  127            	  | False                	 |
| myciel5            |   6           	   | 6                	  | 7200            	  |  True              	   |
| myciel6            | 7              	  | 7                	  | 7200            	  |  True              	   |
| queen5_5           |         5         |          5          |        0.01        |         False          |
| queen6_6           | 7              	  | 7                	  | 0.18             	 |  False              	  |
| queen7_7        	  |         7         | 7                	  | 0.09            	  |  False              	  |
| queen8_8     	     |  9            	   | 9                	  | 5.4             	  | False               	  |
| queen9_9     	     |  10            	  | 10                	 |  120           	   |  False              	  |
| queen8_12     	    |        12         | 12                	 | 2.3              	 |  False              	  |
| queen10_10     	   |        11         | 11                	 | 1295            	  |  False              	  |
| huck               |        11         | 11                	 |  0.36           	  |  False              	  |
| jean               |  10           	   | 10                	 | 0.29             	 |  False              	  |
| david              |  11           	   | 11                	 | 0.17             	 | False               	  |
| anna               |  11           	   | 11                	 | 0.54             	 | False               	  |
| games120  	        |         9         | 9                	  | 0.68             	 | False               	  |
| miles250        	  |         8         | 8                	  |        0.83        | False               	  |
| miles500           |  20           	   | 20                	 | 0.54             	 | False               	  |
| miles750           |  31           	   | 31                	 | 0.56             	 | False               	  |
| miles1000          |  42           	   | 42                	 | 0.66             	 | False               	  |
| miles1500          |  73           	   | 73                	 | 0.55             	 | False               	  |                                                                                                                            |

## Installation & Usage
1. Install IBM CPLEX, setup it for Python
2. Launch `pip install -r requirements.txt`
3. Run `python main.py -p path/to/input/file`. Usage example:
```
usage: main.py [-h] [-p PATH] [-uh] [-t TIME_LIMIT] [-d]

Finds min number of colors for graphs

optional arguments:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to source graph file in .clq format or graph list
                        in .txt format (see README.md for details)
  -t TIME_LIMIT, --time_limit TIME_LIMIT
                        Time limit for processing the graph (in secs)
  -d, --debug           Allow debug prints from cplex


```
- We support either single processing (file should have *.col* extension) or multiple processing (*.txt* extension)
### Multiple input structure
  We expect `.txt` file with the following structure:
```
File,Answer
graph.col,8
...
```
## Sample Output
ToDo
Results (for multiple processing) and logs will be stored in `results/` and `logs/` folders correspondingly
## Developing
1. Run `pip install -r requirements-dev.txt`
2. Setup pre-commit with `pre-commit install
