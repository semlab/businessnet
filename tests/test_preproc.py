import unittest
from test import support
from preproc import ReuterPreproc
from tests.test_data import REUTERS_CORPUS_SAMPLE


class ReuterPreprocTestCase1(unittest.TestCase):

    def test_format_articles(self):
        pp = ReuterPreproc(None)
        res = pp.format_articles(REUTERS_CORPUS_SAMPLE, verbose=False)
        self.assertTrue(len(res) > 0)


class ReuterSGMLPreprocTest(unittest.TestCase):

    def test_reformat_stock_abbr(self):
        text1 = '''
        When I say Microsft &lt;MSFT> I mean compete against Google &lt;GOOG>.
        '''
        text2 = '''
        When I say Microsft [[MSFT]] I mean compete against Google [[GOOG]].
        '''
        prec = ReuterSGMLPreproc()
        formatted = prec.reformat_stock_abbr()
        self.assertEquals(formatted, text2)


if __name__ == "__main__":
    unittest.main()
