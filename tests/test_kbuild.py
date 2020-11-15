import unittest
from test import support
from kbbuild import EntityIdentifier, EdgeBuilder
from tests.test_data import REUTERS_SENTENCES_SAMPLE, OPENIE_SENTENCE_EXTRACTION


class EntityIdentifierTestCase1(unittest.TestCase):

    def test_identify_ents(self):
        identifier = EntityIdentifier()
        identifier.identity_ents(REUTERS_SENTENCES_SAMPLE)
        for ent in identifier.organizations:
            print(ent)
        assert(len(identifier.organizations) > 0)


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



if __name__ == "__main__":
    unittest.main()


