import numpy as np
import networkx as nx
import matplotlib.pyplot as plt 
from collections import Counter
from kgbuild import GraphBuilder
from models import Node


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
                key=len)#, reverse=True)
    max_connected_component = connected_components[len(connected_components)-1]#[0]
    Gmc = G.subgraph(max_connected_component)
    print("Largest Connected Component Info")
    node_type_stats(Gmc)
    #degree_stats(Gmc)
    # TODO: show stats (and draw with colormap)

    # count degree graph
    X = [d['ent_count'] for n,d in G.nodes(data=True) ]
    Y = [G.degree[n] for n in G.nodes()]
    plt.figure(1)
    plt.xlabel("Named Entity Count")
    plt.ylabel("Entity's Node Degree")
    #plt.xscale('log')
    #plt.yscale('log')
    plt.scatter(X,Y, color="blue")

    # Degree histogram highest component
    degree_freq = np.array(nx.degree_histogram(Gmc)).astype('float')
    plt.figure(2)
    plt.stem(degree_freq)
    plt.xlabel("Frequence")
    plt.ylabel("Degree")
    plt.xscale('log')
    plt.yscale('log')

    # Degree histogram hfull component
    degree_freq_all = np.array(nx.degree_histogram(G)).astype('float')
    plt.figure(3)
    plt.stem(degree_freq_all)
    plt.xlabel("Frequence")
    plt.ylabel("Degree")
    plt.xscale('log')
    plt.yscale('log')


    # Biggest Component
    colormap = [Node.color(d['ent_type']) for n,d in Gmc.nodes(data=True)]
    Gmc_orgs = [n for n,d in Gmc.nodes(data=True) if d['ent_type'] == 'ORG']
    Gmc_people = [n for n,d in Gmc.nodes(data=True) if d['ent_type'] == 'PERSON']
    Gmc_places = [n for n,d in Gmc.nodes(data=True) if d['ent_type'] == 'GPE']
    plt.figure(4)
    pos = nx.spring_layout(Gmc)
    nx.draw_networkx_nodes(Gmc, pos=pos, nodelist=Gmc_orgs, node_color='blue', label='Organizations', node_size=25)
    nx.draw_networkx_nodes(Gmc, pos=pos, nodelist=Gmc_people, node_color='red', label='People', node_size=25)
    nx.draw_networkx_nodes(Gmc, pos=pos, nodelist=Gmc_places, node_color='green', label='Places', node_size=25)
    nx.draw_networkx_edges(Gmc, pos=pos, width=0.3)
    plt.legend(scatterpoints = 1)


    connected_component = connected_components[len(connected_components)-2]#[1]
    G2 = G.subgraph(connected_component)
    posG2 = nx.spring_layout(G2)
    node_colors = [Node.color(d['ent_type']) for n,d in G2.nodes(data=True)]
    plt.figure(5)
    nx.draw(G2, pos=posG2, with_labels=True, node_color=node_colors, node_size=30)

    # Component size node count
    components_node_count = [len(component) for component in connected_components]
    #components_node_count = components_node_count.reverse()
    comp_sizes = list(Counter(components_node_count).keys())
    comp_sizes_str = [str(size) for size in comp_sizes]
    comp_sizes_node_count = list(Counter(components_node_count).values())
    print("Number of components: {}".format(len(connected_components)))
    print("Component sizes: {}".format(comp_sizes_str))
    print("Component sizes count: {}".format(comp_sizes_node_count))
    plt.figure(6)
    plt.xlabel('Graph Components Sizes')
    plt.yscale('log')
    plt.bar(comp_sizes_str, comp_sizes_node_count)


    plt.show()