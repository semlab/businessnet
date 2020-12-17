# BuinessNet Builder

## Setup

Install the necessary libraries in requirements.txt

## Run

To build the knowledge graph, two files are needed: A text file formatted as 
one sentence per line (the input file), and a file containing the extraction 
done using OpenIE (the extraction file).

````
python kgbuild.py -i /path/to/sentences.txt -e /path/to/extractions.txt -o /path/to/output-file.json
````

You should also specify the graph output file. 


## Tests 

Run test from the command line, from the top directory 
(where this README file is) using the following command:

````
python -m unittest discover
````