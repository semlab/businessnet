import numpy as np
import networkx as nx
import matplotlib.pyplot as plt 
from kgbuild import GraphBuilder


def node_type_stats(G):
    orgs = [n for n,d in G.nodes(data=True) 
                if 'ent_type' in d 
                and d["ent_type"] == "ORG"]
    people = [n for n,d in G.nodes(data=True)
                if 'ent_type' in d 
                and d['ent_type'] == 'PERSON']
    places = [n for n,d in G.nodes(data=True)
                if 'ent_type' in d 
                and d['ent_type'] == 'GPE']
    nb_orgs = len(orgs)
    nb_people = len(people)
    nb_places = len(places)
    nb_total = nb_orgs + nb_people + nb_places
    print("number of organisations: {}".format(nb_orgs))
    print("number of people: {}".format(nb_people))
    print("number of places: {}".format(nb_places))
    print("Total number of nodes: {}".format(nb_total))
    nb_nodes = G.number_of_nodes()
    if nb_total != nb_nodes:
        print("WARNING: nodes does not add up {} != {}".format(nb_total, nb_nodes))


def degree_stats(G):
    nb_nodes = G.number_of_nodes()
    degree_sequence = list(G.degree())
    degree_array = np.array(degree_sequence)[:,1]
    #avg_degree = np.mean(np.array(degree_sequence)[:,1])
    avg_degree = np.mean(degree_array)
    #med_degree = np.median(degree_array[:,1])
    #max_degree = np.max(degree_array[:,1])
    #min_degree = np.min(degree_array[:,1])
    print("Average Degree{}".format(avg_degree))
    print("Median Degree{}".format(med_degree))
    print("Max Degree{}".format(max_degree))
    print("Min Degree{}".format(min_degree))


if __name__ == "__main__":
    builder = GraphBuilder()
    builder.load_graph("./data/graph_node_link.json")
    # filtering out empty nodes
    G = builder.G
    nodes = [n for n,d in G.nodes(data=True) if len(d.keys()) > 0 ]
    builder.G = G.subgraph(nodes)
    G = builder.G
    print("Full Graph Info")
    node_type_stats(G)
    #degree_stats(G)
    connected_nodes = [n for n in G.nodes if G.degree[n] > 0]
    Gc = G.subgraph(connected_nodes)
    print("Connected Graph Info")
    node_type_stats(Gc)
    #degree_stats(Gc)
    # TODO: show stats (and draw with colormap)
    connected_components = sorted(nx.connected_components(Gc), 
                key=len, reverse=True)
    max_connected_component = connected_components[0]
    Gmc = G.subgraph(max_connected_component)
    print("Largest Connected Component Info")
    node_type_stats(Gmc)
    #degree_stats(Gmc)
    # TODO: show stats (and draw with colormap)


    #TODO: count degree graph
    X = [d['ent_count'] for n,d in G.nodes(data=True) ]
    Y = [G.degree[n] for n in G.nodes()]
    plt.figure(1)
    plt.xlabel("Named Entity Count")
    plt.ylabel("Entity's Node Degree")
    plt.scatter(X,Y, color="blue")
    plt.show()