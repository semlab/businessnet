import unittest
import matplotlib.pyplot as plt
import networkx as nx
from test import support
from kbbuild import EntityIdentifier, EdgeBuilder, GraphBuilder, Node, Edge
from tests.test_data import REUTERS_SENTENCES_SAMPLE, OPENIE_SENTENCE_EXTRACTION


class EntityIdentifierTestCase1(unittest.TestCase):

    def test_identify_ents(self):
        identifier = EntityIdentifier()
        identifier.identity_ents(REUTERS_SENTENCES_SAMPLE)
        #for ent in identifier.nodes:
        #    print(ent)
        assert(len(identifier.nodes) > 0)


    def test_id_from_name(self):
        name = "an International Development Association"
        id_name  = EntityIdentifier.id_from_name(name)
        assert(id_name == "international-development-association")

class EdgeBuilderTestCase1(unittest.TestCase):

    def test_sent_edges_build(self):   
        openie_sample = OPENIE_SENTENCE_EXTRACTION.split('\n')
        sentence = openie_sample[0]
        extractions = openie_sample[1:]
        ebuilder = EdgeBuilder()
        edges = ebuilder.sent_edges_build(sentence, extractions)
        assert(len(edges) == 3)


class GraphBuilderTestCase(unittest.TestCase):

    def test_build(self):
        nodes = []
        nodes.append(Node("apple", "ORG", "Apple"))
        nodes.append(Node("tim-cook", "PERSON", "Tim Cook"))
        nodes.append(Node("san-francisco", "GPE", "San Francisco"))
        edges = []
        edges.append(Edge("apple", "tim-cook", "OTHER", "is CEO"))
        edges.append(Edge("apple", "san-francisco", "OTHER", "has Headquarter in"))
        builder = GraphBuilder(nodes, edges)
        G = builder.build()
        nx.draw(G, with_labels=True)
        plt.show()
        assert(G.number_of_nodes() == 3)
        assert(G.number_of_edges() == 2)




if __name__ == "__main__":
    unittest.main()


