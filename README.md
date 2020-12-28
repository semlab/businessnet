# BuinessNet Builder

## Setup

Install the necessary libraries in requirements.txt

```
pip install -r requirements.txt
```

## Run

### kgbuild

To build the knowledge graph, two files are needed: A text file formatted as 
one sentence per line (the input file), and a file containing the extraction 
done using [OpenIE](https://github.com/dair-iitd/OpenIE-standalone) (the extraction file).
You should also specify the graph output (json) file. 

````
python kgbuild.py -i /path/to/sentences.txt -e /path/to/extractions.txt -o /path/to/output-file.json
````


## Tests 

Run test from the command line, from the top directory 
(where this README file is) using the following command:

````
python -m unittest discover
````