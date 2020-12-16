import unittest
from test import support
from preproc import ReuterPreproc
from tests.test_data import REUTERS_CORPUS_SAMPLE


class ReuterPreprocTestCase1(unittest.TestCase):

    def test_format_articles(self):
        pp = ReuterPreproc(None)
        res = pp.format_articles(REUTERS_CORPUS_SAMPLE, verbose=False)
        self.assertTrue(len(res) > 0)


if __name__ == "__main__":
    unittest.main()