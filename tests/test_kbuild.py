import unittest
import matplotlib.pyplot as plt
import networkx as nx
from test import support
from models import Node, Edge
from kbbuild import EntityIdentifier, EdgeBuilder, GraphBuilder
from tests.test_data import REUTERS_SENTENCES_SAMPLE, OPENIE_SENTENCE_EXTRACTION


class EntityIdentifierTestCase1(unittest.TestCase):

    def test_identify_ents(self):
        identifier = EntityIdentifier()
        identifier.identity_ents(REUTERS_SENTENCES_SAMPLE)
        #for ent in identifier.nodes:
        #    print(ent)
        self.assertTrue(len(identifier.nodes) > 0)


    def test_id_from_name(self):
        name = "an International Development Association"
        id_name  = EntityIdentifier.id_from_name(name)
        self.assertEqual(id_name, "international-development-association")

class EdgeBuilderTestCase1(unittest.TestCase):

    def test_sent_edges_build(self):   
        openie_sample = OPENIE_SENTENCE_EXTRACTION.split('\n')
        sentence = openie_sample[0]
        extractions = openie_sample[1:]
        ebuilder = EdgeBuilder()
        edges = ebuilder.sent_edges_build(sentence, extractions)
        self.assertEqual(len(edges), 3)


class GraphBuilderTestCase(unittest.TestCase):

    def setUp(self):
        nodes = []
        nodes.append(Node("apple", "ORG", "Apple"))
        nodes.append(Node("tim-cook", "PERSON", "Tim Cook"))
        nodes.append(Node("san-francisco", "GPE", "San Francisco"))
        nodes.append(Node("google", "ORG", "Google"))
        edges = []
        edges.append(Edge("apple", "tim-cook", "OTHER", "is CEO"))
        edges.append(Edge("apple", "san-francisco", "OTHER", "has Headquarter in"))
        edges.append(Edge("google", "san-francisco", "OTHER", "has Headquarter in"))
        self.builder = GraphBuilder()
        self.builder.build(nodes, edges)

    #def tearDown(self):
    #    self.builder.dispose()

    def test_node_count(self):
        self.assertEqual(self.builder.G.number_of_nodes(), 4)
    
    def test_edge_count(self):
        self.assertEqual(self.builder.G.number_of_edges(),  3)

    def test_subgraph(self):
        org_graph = self.builder.subgraph('ORG')
        self.assertEqual(org_graph.number_of_nodes(), 2)




if __name__ == "__main__":
    unittest.main()


