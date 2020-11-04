import unittest
from test import support
from kbbuild import EntityIdentifier
from tests.test_data import REUTERS_SENTENCES_SAMPLE


class EntityIdentifierTestCase1(unittest.TestCase):

    def test_identify_ents(self):
        identifier = EntityIdentifier()
        identifier.identity_ents(REUTERS_SENTENCES_SAMPLE)
        assert(len(identifier.organizations) > 0)


if __name__ == "__main__":
    unittest.main()


