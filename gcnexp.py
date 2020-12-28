import itertools
import random
from collections import Counter
import dgl
import networkx as nx
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from dgl.nn.pytorch import GraphConv
from kgbuild import GraphBuilder


class GCN(nn.Module):

    def __init__(self, in_feats, hidden_size, num_classes):
        super(GCN, self).__init__()
        self.conv1 = GraphConv(in_feats, hidden_size)
        self.conv2 = GraphConv(hidden_size, num_classes)

    def forward(self, g, inputs):
        h = self.conv1(g, inputs)
        h = torch.relu(h)
        h = self.conv2(g, h)
        return h


def type2label(label):
    if label == "ORG":
        return 0
    elif label == 'PERSON':
        return 1
    elif label == 'GPE':
        return 2
    return None

def draw(i):
    cls1color = 'blue'
    cls2color = 'red'
    cls3color = 'green'
    pos = {}
    colors = []
    for v in range(nb_nodes):
        pos[v] = all_logits[i][v].numpy()
        cls = pos[v].argmax()
        color = 'gray'
        if cls == 0:
            color = cls1color
        elif cls == 1:
            color = cls2color
        elif cls == 2:
            color == cls3color
        colors.append(color)
    ax.cla()
    ax.axis('off')
    #ax.set_title('Epoch: %d:' % i)
    #nx.draw_networkx(G, pos, node_color=colors, node_size=300, ax=ax)
    nx.draw_networkx(G, node_color=colors, 
            #with_labels=False,
            pos=nx.spring_layout(G),
            node_size=30, 
            ax=ax)


if __name__ == "__main__":
    builder = GraphBuilder()
    builder.load_graph("./data/graph_node_link.json")
    # filtering out empty nodes TODO A la construction du graph
    G = builder.G
    nodes = [n for n,d in G.nodes(data=True) if len(d.keys()) > 0 ]
    builder.G = G.subgraph(nodes)
    G = builder.G

    connected_components = sorted(nx.connected_components(G), 
        key=len, reverse=True)
    component = connected_components[1]
    G = G.subgraph(component)
    nb_nodes = G.number_of_nodes()
    print("Number of nodes: {}".format(nb_nodes))
    
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

    lbl_orgs = random.sample(orgs, int(nb_orgs*0.10)) # using 10% of orgs to be labelled
    lbl_people = random.sample(people, int(nb_people*0.10)) # 10% of labelled people
    lbl_places = random.sample(places, int(nb_places*0.10)) # 10% of labelled places

    lbl_nodes = np.concatenate(( lbl_orgs, lbl_people, lbl_places), axis=0) 
    labels_lst = np.concatenate((
        np.full(len(lbl_orgs), 0), # orgs are labelled 0
        np.full(len(lbl_people), 1), # people are labelled 1
        np.full(len(lbl_places), 2) # places are labelled 2
    ), axis=0)

    dG = dgl.from_networkx(G)
    embed = nn.Embedding(nb_nodes, 5)
    dG.ndata['feat'] = embed.weight
    net = GCN(5,5,3)
    inputs = embed.weight
    labeled_nodes = torch.tensor(lbl_nodes)
    labels = torch.tensor(labels_lst)
    optimizer = torch.optim.Adam(itertools.chain(net.parameters(), 
            embed.parameters()),
            lr=0.02)
    all_logits = []
    for epoch in range(100):
        logits = net(dG, inputs)
        all_logits.append(logits.detach())
        logp = F.log_softmax(logits, 1)
        loss = F.nll_loss(logp[labeled_nodes], labels)
        optimizer.zero_grad()
        loss.backward()
        optimzer.step()
        print("Epoch %d | Loss: %.4f" % (epoch, loss.item()))
##########

    nb_labeled = int(len(node_labels) * 0.25) # using 25% of nodes to be labelled
    labeled_nodes_lst = []
    while len(list(Counter(labeled_nodes_lst).keys())) < 3:
        labeled_nodes_lst = random.sample(node_idxs, nb_labeled)
    labels_lst = [node_labels[i] for i in labeled_nodes_lst]
    
    dG = dgl.from_networkx(G)
    embed = nn.Embedding(nb_nodes, 5)
    dG.ndata['feat'] = embed.weight
    net = GCN(5,5,3)
    inputs = embed.weight
    labeled_nodes = torch.tensor(labeled_nodes_lst) 
    labels = torch.tensor(labels_lst) 

    optimizer = torch.optim.Adam(itertools.chain(net.parameters(), 
            embed.parameters()), 
            lr=0.01)
    all_logits = []
    for epoch in range(100):
        logits = net(dG, inputs)
        all_logits.append(logits.detach())
        logp = F.log_softmax(logits, 1)
        loss = F.nll_loss(logp[labeled_nodes], labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print('Epoch %d | Loss: %.4f' % (epoch, loss.item()))

    fig = plt.figure(dpi=150)
    fig.clf()
    ax = fig.subplots()
    
    draw(99)
    #ani = animation.FuncAnimation(fig, draw, frames=len(all_logits), interval=200)
    plt.show()



