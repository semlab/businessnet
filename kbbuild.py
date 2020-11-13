import re
import json
from lang import LangModel
from utils import printProgressBar


class NodeType:
    ORG = "ORG"
    PERSON = "PERSON"
    PLACE = "GPE"
    Set = {"ORG", "PERSON", "GPE"}


class EdgeType:
    TRADE = "TRADE"
    OTHER = "OTHER"
    Set = {"TRADE", "OTHER"}


class Node:

    def __init__(self, ent_id, ent_type, ent_label):
        self.ent_id = ent_id
        self.ent_type = ent_type
        self.ent_label = ent_label 

class NodeJSONEncoder(JSONEncoder):

    def default(self, o):
        return o.__dict__

class Edge:

    def __init__(self, ent1_id, ent2_id, rel_type, rel_label):
        self.ent1_id = ent1_id
        self.ent2_id = ent2_id
        self.rel_type = rel_type
        self.rel_label = rel_label

class EntityIdentifier:

    def __init__(self):
        self.organizations = []
        self.people = []
        self.places = []
        self.nodes = []

    def identity_ents(self, text):
        nlp = LangModel.get_instance()
        doc = nlp(text)
        orgs = []
        people = []
        places = []
        nodes = []
        for ent in doc.ents:
            ent_id = self.id_from_name(ent.text)
            if len(ent_id) < 3: continue
            if ent.label_ == 'ORG':
                orgs.append(ent_id)
            elif ent.label_ == 'PERSON':
                people.append(ent_id)
            elif ent.label_ == 'GPE':
                places.append(ent_id)
            # for file
            if ent.label_ in NodeType.Set:
                nodes.append(Node(ent_id, ent.label_, ent.text))
        #orgs = list(set(orgs))
        #people = list(set(people))
        #places = list(set(places))
        self.organizations.extend(orgs)
        self.people.extend(people)
        self.places.extend(places)
        self.nodes.extend(nodes)


    #def id_from_name(self, ent_name):
    @staticmethod
    def id_from_name(ent_name):
        id_label = ent_name.lower().strip()
        if id_label.startswith("the "): 
            id_label = id_label[4:]
        elif id_label.startswith("an "):
            id_label = id_label[3:]
        id_label = id_label.replace("'s", "") 
        id_label = id_label.replace(".", "") 
        id_label = id_label.replace(",", "") 
        id_label = id_label.replace("(", "") 
        id_label = id_label.replace(")", "") 
        id_label = id_label.replace("<", "") 
        id_label = id_label.replace(">", "") 
        id_label = id_label.replace("\"", "") 
        id_label = id_label.replace("/", "-") 
        id_label = id_label.replace("'", "") 
        id_label = id_label.replace(" ", "-") 
        id_label = id_label.replace(" ", "") # remove all left spaces
        id_label = id_label.strip("- ")
        #TODO: remove trailing dash and multiple dashes
        return id_label
    
    def remove_duplicate(self):
        self.organizations = list(set(self.organizations))
        self.people = list(set(self.people))
        self.places = list(set(self.places))
        # making nodes elements uniques
        nodes = self.nodes
        start_idx = 0
        while start_idx < len(nodes):
            node_idx = start_idx + 1
            while node_idx < len(nodes):
                if nodes[start_idx].ent_id == nodes[node_idx].ent_id:
                    del nodes[node_idx]
                else:
                    node_idx += 1
            start_idx += 1
            printProgressBar(start_idx, len(nodes), prefix="Unifiying nodes ")
        self.nodes = nodes


    def save_ents(self):
        print("saving {} orgs".format(len(self.organizations)))
        with open('./data/orgs.txt', 'w') as orgfile:
            for org in self.organizations:
                orgfile.write(org + '\n')
        print("saving {} persons".format(len(self.people),))
        with open('./data/people.txt', 'w') as peoplefile:
            for person in self.people:
                peoplefile.write(person + '\n')
        print("saving {} places".format(len(self.places)))
        with open('./data/places.txt', 'w') as placesfile:
            for place in self.places:
                placesfile.write(place + '\n')
        print("saving {} nodes".format(len(self.nodes)))
        with open("./data/nodes.txt", 'w') as nodesfile:
            json.dump(self.nodes, nodesfile, indent=6)



class EdgeBuilder:
    """
    Build relationships from OpenIE output
    """

    def __init__(self): 
        self.edges = []
       

    def edges_build(self, inputpath):
        edges = []
        lines = []
        with open(inputpath, 'r') as inputfile:
            lines = inputfile.readlines()
        line_iter = 0
        lines_count = len(line_iter)
        while line_iter < lines_count:
            sent_txt = lines[line_iter]
            line_iter += 1 # to point sentence's extractions
            sent_extracts = []
            while line_iter < lines_count and lines[line_iter] != "":
                sent_extracts.append(lines[line_iter])
                line_iter += 1
            sent_edges = sent_edges_build(sent_txt, sent_extracts)
            edges.extend(sent_edges)
            printProgressBar(line_iter, lines_count, 
                prefix="Building Edges")
            line_iter += 1 # to point next sentence
        self.edges = edges
        return edges


    def sent_edges_build(self, sent_txt, extractions):
        edges = []
        extract_pattern = re.compile(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$")
        nlp = LangModel.get_instance()
        doc  = nlp(sent_txt)
        ents = [e for e in doc.ents if e.label_ in NodeType.Set] 
        if len(ents) < 2:
            return edges
        for extraction in extractions:
            if extract_pattern.match(extraction) is not None:
                extract_str = extraction[4:-1]
                extract_parts = extract_str.split(';')
                ent1 = None
                ent2 = None
                rel = None
                for ent in ents:
                    if ent.string in extract_parts[0]:
                        #TODO: retrieve unique id of ent
                        ent1 = ent
                    elif ent.string in extract_parts[2]:
                        #TODO: retrieve unique id of ent
                        ent2 = ent
                #TODO: Retrieve edge type trade/other id
                rel = EdgeType.OTHER
                if ent1 is not None and ent2 is not None and rel is not None:
                    edges.append([ent1, rel, ent2])
        return edges



    def triplets_filter(self, inputfilepath, outputfilepath):
        """
        Filter OpenIE output file to keep
        interesting triplets
        """
        triplet_file_content = ""
        with open(inputfilepath, 'r') as inputfile:
            triplet_file_content = inputfile.read()
        triplets = re.findall(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$", triplet_file_content)
        for idx, triplet in triplets:
            pass
        pass



class GraphBuilder:

    def __init__(self):
        pass
    



if __name__ == "__main__":
    identifier = EntityIdentifier()
    sents_count = 0
    with open('./data/reuter_sentences.txt', 'r') as textfile:
        text = textfile.readline()
        while text :
            sents_count = sents_count + 1
            identifier.identity_ents(text) 
            text = textfile.readline()
            print(f'\r{sents_count} sentences processed', end='')
    print()
    identifier.remove_duplicate()
    identifier.save_ents()
    
    
