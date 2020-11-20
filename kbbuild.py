import re
import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from lang import LangModel
from models import Node, Edge, NodeType, EdgeType
from utils import printProgressBar


class EntityIdentifier:

    def __init__(self):
        self.nodes = []

    def identity_ents(self, text):
        nlp = LangModel.get_instance()
        nodes_dict = {}
        doc = nlp(text)
        for ent in doc.ents:
            ent_id = self.id_from_name(ent.text)
            if len(ent_id) < 3: continue
            if ent.label_ in NodeType.Set and ent_id not in nodes_dict:
                nodes_dict[ent_id] = Node(ent_id, ent.label_, ent.text)
        nodes = list(nodes_dict.values())
        self.nodes.extend(nodes)
        return self.nodes


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
    
    # TODO: delete useless
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
        print("saving {} nodes".format(len(self.nodes)))
        with open("./data/nodes.txt", 'w') as nodesfile:
            json.dump(self.nodes, nodesfile, indent=6, default=str)


class EdgeBuilder:
    """
    Build relationships from OpenIE output
    """
    def __init__(self): 
        self.edges = []
       

    def edges_build(self, inputpath):
        edges_dict = {}
        #edges = []
        lines = []
        with open(inputpath, 'r') as inputfile:
            lines = inputfile.readlines()
        line_iter = 0
        lines_count = len(lines)
        while line_iter < lines_count:
            sent_txt = lines[line_iter]
            line_iter += 1 # to point sentence's extractions
            sent_extracts = []
            while line_iter < lines_count and lines[line_iter] != "\n":
                sent_extracts.append(lines[line_iter])
                line_iter += 1
            sent_edges = self.sent_edges_build(sent_txt, sent_extracts)
            for edge in sent_edges:
                edge_key = "{}_{}".format(edge.ent1_id, edge.ent2_id)
                if edge_key  not in edges_dict:
                    edges_dict[edge_key] = edge
            printProgressBar(line_iter, lines_count)
            line_iter += 1 # to point next sentence
        print()
        edges = list(edges_dict.values())
        self.edges = edges
        return self.edges


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
                ent1_id = None
                ent2_id = None
                rel_label = None
                rel_type = None
                for ent in ents:
                    if ent.string in extract_parts[0]:
                        ent1_id = EntityIdentifier.id_from_name(ent.string)
                    elif ent.string in extract_parts[2]:
                        ent2_id = EntityIdentifier.id_from_name(ent.string)
                rel_label = extract_parts[1]
                #TODO: Retrieve edge type trade/other id
                rel_type = EdgeType.OTHER
                if ent1_id is not None and ent2_id is not None and rel_type is not None:
                    edge = Edge(ent1_id, ent2_id, rel_type, rel_label)
                    edges.append(edge)
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


    def remove_duplicate(self):
        pass



class GraphBuilder:

    def __init__(self):
        self.G = nx.Graph()
        self.colormap = None

    def build(self, nodes, edges):
        nodes_list = [(node.ent_id, node.__dict__) for node in nodes]
        edges_list = [(edge.ent1_id, edge.ent2_id, {
                "label": edge.rel_label,
                "type": edge.rel_type
            }) for edge in edges]
        self.G.add_nodes_from(nodes_list)
        self.G.add_edges_from(edges_list)
        return self.G

    def subgraph(self, node_type):
        if node_type not in NodeType.Set:
            return None
        orgs_nodes = [node in G.nodes] #if node['ent_type'] == node_type ]
        return self.G.subgraph(orgs_nodes)
    
    def save_graph(self, filename):
        data = json_graph.node_link_data(self.G)
        file_content = json.dumps(data)
        with open(filenanme, 'w') as outfile: 
            outfile.write(file_content)
    
    def load_graph(self, filename):
        file_content = ""
        with open(filename, 'r') as infile:
            file_content = infile.read()
        data = json.loads(file_content)
        self.G = json_graph.node_link_graph(data)




    
# for tests in the shell
def build_the_graph():
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
#    identifier.remove_duplicate()
    identifier.save_ents()
    nodes = identifier.nodes

    ebuilder = EdgeBuilder()
    edges = ebuilder.edges_build("./data/reuter_openie_out.txt")    
    print("Number of edges: {}".format(len(edges)))

    print("Building graph {} nodes, {} edges".format(len(nodes), len(edges)))
    gbuilder = GraphBuilder()
    G = gbuilder.build(nodes, edges)
    return G



if __name__ == "__main__":
    # --sentences="sentences inpout text file"
    # --extractions="openie extractions"
    # --openie-run="openie run command (for external call)"
    # --output="graph output file name"
    # TODO: Verify existence of input data
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
#    identifier.remove_duplicate()
    identifier.save_ents()
    nodes = identifier.nodes

    ebuilder = EdgeBuilder()
    edges = ebuilder.edges_build("./data/reuter_openie_out.txt")    
    print("Number of edges: {}".format(len(edges)))

    print("Building graph {} nodes, {} edges".format(len(nodes), len(edges)))
    gbuilder = GraphBuilder()
    G = gbuilder.build(nodes, edges)
    #color_map = []
    #for node in G:
    #    color = Node.color( node['ent_type'])
    #    color_map.append(color)
    #nx.draw(G, node_color=color_map)#, with_labels=True)


    nx.draw(G, with_labels=False)
    plt.show()

    
    
