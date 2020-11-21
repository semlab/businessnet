import unittest 
from test import support 
from lang import LangModel


class LangModelTestCase1(unittest.TestCase):

    def test_get_instance(self):
        nlp = LangModel.get_instance()
        self.assertTrue(nlp is not None)