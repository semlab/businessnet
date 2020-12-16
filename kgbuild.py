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
        self.nodes_dict = {}

    def identify_ents(self, text):
        nlp = LangModel.get_instance()
        doc = nlp(text)
        for ent in doc.ents:
            ent_id = self.id_from_name(ent.text)
            if len(ent_id) < 3: continue
            if ent.label_ in NodeType.Set and ent_id not in self.nodes_dict:
                self.nodes_dict[ent_id] = Node(ent_id, ent.label_, ent.text, 1)
            elif ent_id in self.nodes_dict:
                self.nodes_dict[ent_id].ent_count += 1
        nodes = list(self.nodes_dict.values())
        nodes = [n for n in nodes if isinstance(n, Node)] 
        self.nodes = nodes
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
        #TODO: remove multiple dashes
        return id_label
    

class NodeLookup:

    def __init__(nodes):
        """
         nodes from EntityIdentifier
        """
        # TODO: find a way to ensure that enumerate give the same ids
        # for the same nodes in lookup (here) and in graphbuilder
        self.labelids = {}
        self.indexes = {}
        for idx,node in enumerate(nodes):
            labelids[idx] = node.id
            indexes[node.id] = idx
            
    def get_labelid(index):
        return self.labelids[index]

    def get_index(labelid):
        return self.indexes[labelid]


class EdgeBuilder:
    """
    Build relationships from OpenIE output
    """
    def __init__(self, nodelookup = None):
        self.edges = []
        self.nodelookup = nodelookup
       

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
        nodelookup = self.nodelookup
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
                    if nodelookup is not None:
                        ent1_idx = nodelookup.get_index(ent1_id)
                        ent2_idx = nodelookup.get_index(ent2_id)
                        edge = Edge(ent1_idx, ent2_id2, rel_type, rel_label)
                    else:
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



class GraphBuilder:

    def __init__(self):
        self.G = nx.Graph()


    def build(self, nodes, edges):
        print("\nLES NOMBRE NODES:", len(nodes))
        nodes_list = [(idx, n.__dict__) for idx,n in enumerate(nodes)]
        print("LONGUEUR NODE LIST: ", len(nodes_list))
        print(nodes_list)
        edges_list = [(edge.ent1_id, edge.ent2_id, {
                "label": edge.rel_label,
                "type": edge.rel_type
        }) for edge in edges]
        self.G.add_nodes_from(nodes_list)
        self.G.add_edges_from(edges_list)
        print("LES NODES IN GRAPHS: ", self.G.number_of_nodes())
        return self.G


    def build_colormap(self, G = None):
        colormap = []
        if G is None:
            G = self.G
        for node_id, node_data in G.nodes(data=True):
            print(node_data)
            color = 'gray'
            if 'ent_type' in node_data:
                ent_type = node_data['ent_type']
                color = Node.color(ent_type)
            colormap.append(color)
        return colormap


    # TODO: delete
    def subgraph_back(self, node_type):
        if node_type not in NodeType.Set:
            return None
        nodes_subset = []
        for node_id in self.G:
            node_data = self.G.nodes[node_id]
            if node_data['ent_type'] == node_type:
                nodes_subset.append(node_id)
        return self.G.subgraph(nodes_subset)


    def subgraph(self, node_type=None, count_filter=0):
        if node_type is not None and node_type not in NodeType.Set:
            return None
        G = self.G
        nodes_subset = []
        if node_type in NodeType.Set and count_filter > 0:
            nodes_subset = [n for n,d in G.nodes(data=True) 
                                if 'ent_type' in d
                                and 'ent_count' in d
                                and d['ent_type'] == node_type and 
                                d['ent_count'] >= count_filter]
        elif node_type in NodeType.Set and count_filter <= 0:
            nodes_subset = [n for n,d in G.nodes(data=True)
                                if 'ent_type' in d 
                                and d['ent_type'] == node_type]
        elif node_type is None and count_filter > 0:
            nodes_subset = [n for n,d in G.nodes(data=True) 
                                if 'ent_count' in d 
                                and  d['ent_count'] >= count_filter]
        return self.G.subgraph(nodes_subset)
    
    def save_graph(self, filename):
        data = json_graph.node_link_data(self.G)
        file_content = json.dumps(data)
        with open(filename, 'w') as outfile: 
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
            identifier.identify_ents(text) 
            text = textfile.readline()
            print(f'\r{sents_count} sentences processed', end='')
    print()
    #identifier.save_ents()
    nodes = identifier.nodes

    nodelookup = NodeLookup(nodes)

    ebuilder = EdgeBuilder(nodelookup)
    #edges = ebuilder.edges_build("./data/reuter_openie_out.txt")    
    edges = ebuilder.edges_build("./data/reuter_sentences_out.txt")    
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
            identifier.identify_ents(text) 
            text = textfile.readline()
            print(f'\r{sents_count} sentences processed', end='')
    print()
    #identifier.save_ents()
    nodes = identifier.nodes

    nodelookup = NodeLookup(nodes)

    ebuilder = EdgeBuilder(nodelookup)
    #edges = ebuilder.edges_build("./data/reuter_openie_out.txt")    
    edges = ebuilder.edges_build("./data/reuter_sentences_out.txt")    
    print("Number of edges: {}".format(len(edges)))

    print("Building graph {} nodes, {} edges".format(len(nodes), len(edges)))
    gbuilder = GraphBuilder()
    G = gbuilder.build(nodes, edges)
    gbuilder.save_graph("./data/graph_node_link.json")
    O = gbuilder.subgraph('ORG')
    #nx.draw(G)
    #plt.show()

    
    
