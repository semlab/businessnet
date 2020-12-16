import unittest
import matplotlib.pyplot as plt
import networkx as nx
from test import support
from models import Node, Edge
from kgbuild import EntityIdentifier, EdgeBuilder, GraphBuilder, NodeLookup
from tests.test_data import REUTERS_SENTENCES_SAMPLE, OPENIE_SENTENCE_EXTRACTION
from tests.test_data import SAMPLE_NODES, SAMPLE_EDGES


class EntityIdentifierTestCase1(unittest.TestCase):

    def test_identify_ents(self):
        identifier = EntityIdentifier()
        identifier.identify_ents(REUTERS_SENTENCES_SAMPLE)
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

class NodeLookupTestCase1(unittest.TestCase):

    def setUp(self):
        self.nodelookup = NodeLookup(SAMPLE_NODES)

    def test_get_labelid(self):
        self.assertEqual(
            self.nodelookup.get_labelid(0), "apple") 

    def test_get_index(self):
        self.assertEqual( self.nodelookup.get_index("apple"), 0)


class GraphBuilderTestCase(unittest.TestCase):

    def setUp(self):
        # TODO: use lookup table
        # TODO: test lookup table
        nodes = SAMPLE_NODES
        edges = SAMPLE_EDGES
        self.builder = GraphBuilder()
        self.builder.build(nodes, edges)

    def tearDown(self):
        self.builder.G.clear()

    def test_node_count(self):
        self.assertEqual(self.builder.G.number_of_nodes(), 4)
    
    def test_edge_count(self):
        self.assertEqual(self.builder.G.number_of_edges(),  3)

    def test_subgraph(self):
        org_graph = self.builder.subgraph('ORG')
        self.assertEqual(org_graph.number_of_nodes(), 2)

    def test_build_colormap(self):
        self.builder.build_colormap()
        self.assertEqual(self.builder.G.number_of_nodes(), len(self.builder.build_colormap()))

    def test_draw(self):
        G = self.builder.G
        colormap = self.builder.build_colormap()
        nx.draw(G, node_color=colormap, pos=nx.random_layout(G), with_labels=True)
        plt.savefig('./data/test_graph.pdf')



if __name__ == "__main__":
    unittest.main()


