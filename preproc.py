#!/usr/bin/python3

import os
import re
import spacy 
import xml.etree.ElementTree as ET
from io import StringIO

from lang import LangModel



class ReuterSGMDoc():

    P_TABLE = re.compile("(  +.+\n){3,}")
    P_STOCKID = re.compile('&lt;(?P<abbr>\w*)>')
    P_HTMLENTS = re.compile('&#[0-9]*;')

    def __init__(self, sgm_content=None):
        self.sgm = sgm_content
        self.sgml = None
        self.txt = None


    def align_sents(self, text):
        """Put one sentence per line"""
        lines = text
        lines = lines.replace(".\n", ".<br/>")
        lines = lines.replace("\n", " ")
        lines = lines.replace("<br/>", "\n")
        return lines


    def format_stockid(self, text): 
        """
        Find and replace stock abbreviation enclosing 
        to avoid parsing error
        Using (stockabbr) to enclose non tag content like stocks name
        """
        # &lt;NAME>  -> (NAME)
        # abbr is the stock abbreviation
        formatted_text = ReuterSGMDoc.P_STOCKID.sub(r'(\g<abbr>)', text)
        return formatted_text 


    def find_table(self, text):
        """Find 'formatted' table in the text"""
        result = ReuterSGMDoc.P_TABLE.search(text)
        return result


    def load_sgm(self, filepath):
        with open(filepath, 'r') as f:
            try:
                self.sgm = f.read()
            except UnicodeDecodeError:
                print("Error decoding {}.".format(filepath))
                self.sgm = None


    def laod_sgml(self, filepath):
        with open(filepath, 'r') as f:
            self.sgml = f.read()


    def laod_txt(self, filepath):
        with open(filepath, 'r') as f:
            self.txt = f.read()


    def save_sgml(self, filepath):
        if self.sgml is None:
            self.to_sgml()
        with open(filepath, 'w') as f:
            if self.sgml is not None:
                f.write(self.sgml)


    def save_txt(self, filepath, solve_coref=False):
        if self.txt is None:
            self.to_txt(solve_coref)
        with open(filepath, 'w') as f:
            if self.txt is not None:
                f.write(self.txt)


    def remove_tables(self, text):
        """Remove table from the text (plain text)"""
        return ReuterSGMDoc.P_TABLE.sub('\n', text)
        

    def to_sgml(self):
        """Format the SGML file making it xml parser friendly"""
        if self.sgml is not None:
            return self.sgml
        if self.sgm is None:
            print('Warning: no content to format')
            return None
        formatted_text = self.format_stockid(self.sgm)
        # remove trailing 'Reuter' at the end of articles
        formatted_text = formatted_text.replace("Reuter\n&#3;</BODY>", 
            "\n</BODY>")
        # remove unknown html entities
        formatted_text = ReuterSGMDoc.P_HTMLENTS.sub(r'',formatted_text)
        formatted_text = formatted_text.replace(
                '<!DOCTYPE lewis SYSTEM "lewis.dtd">',
                '<!DOCTYPE lewis SYSTEM "lewis.dtd">\n<SGML>')
        formatted_text = '\n'.join([formatted_text, "\n</SGML>"])
        self.sgml = formatted_text
        return self.sgml


    def to_txt(self, solve_coref=False): 
        """
        :parameter solve_coref: should the coreference be solved 
        :returns: a one sentence per line string
        """
        if self.sgm is None and self.sgml is None:
            print('Warning: no content to format')
            return None
        if self.txt is not None:
           return self.txt
        if self.sgml is None:
            self.sgml = self.to_sgml()
        text_content = []
        root = ET.fromstring(self.sgml)
        for body in root.iter("BODY"):
            text = self.remove_tables(body.text)
            if (text.startswith("Shr ") or text.startswith("Oper ")  
                    or text.startswith("Qtly ") or text.startswith("Qtr ") 
                    or text.startswith("Qtrly ")): #TODO use regexp
                continue
            text = self.align_sents(text)
            text = text.replace("    ", "") #TODO use regexp (2+)space
            text_content.append(text)
        self.txt =  "\n\n".join(text_content)
        if solve_coref:
            self.txt = self.solve_coref()
        return self.txt


    def solve_coref(self):
        """Solve the coreference on the text content"""
        nlp = LangModel.get_instance()
        text = self.to_txt()
        doc = nlp(text)
        tok_list = list(token.text_with_ws for token in doc)
        for cluster in doc._.coref_clusters:
            cluster_main_words = set(cluster.main.text.split(' '))
            for coref in cluster:
                if coref != cluster.main.text and bool(set(coref.text.split(' ')).intersection(cluster_main_words)) == False:
                    tok_list[coref.start] = cluster.main.text + doc[coref.end - 1].whitespace_
                    for i in range(coref.start + 1, coref.end):
                        tok_list[i] = ""
        self.txt = "".join(tok_list)
        return self.txt

    # Actually useless
    def sents_tokens(self):
        # TODO can be written as actual generator/iterator
        text = self.to_txt()
        nlp = LangModel.get_instance()
        doc = nlp(text)
        tokens_list = []
        for sent in doc.sents:
            tokens_list = [tk.text.lower() for tk in sent 
                if not tk.is_stop and tk.is_alpha and len(tk.text) > 1]
            tokens_list.append(tokens)
        return tokens_list


class ReuterDSConverter():
    """ Reuter Data set Converter
    Manage the convertion of the dataset from one format to another.
    """

    SGM_FORMAT = 'sgm'
    SGML_FORMAT = 'sgml'
    TXT_FORMAT = 'txt'

    def __init__(self, infolder=".", outfolder="."):
        self.infolder = infolder
        self.outfolder = outfolder

    def convert(self, informat, outformat):
        if informat not in [self.SGM_FORMAT, self.SGML_FORMAT]: 
              raise ValueError("Possible input format are: {}, {}", 
                  self.SGM_FORMAT, self.SGML_FORMAT)
        if outformat not in [self.SGML_FORMAT, self.TXT_FORMAT]:
              raise ValueError("Possible output format are: {}, {}",
                  self.SGML_FORMAT, self.TXT_FORMAT)
        for filename in os.listdir(self.infolder):
            if filename.endswith("."+informat):
               infilepath = os.path.join(self.infolder, filename)
               sgmdoc = ReuterSGMDoc() 
               if informat == self.SGM_FORMAT:
                   sgmdoc.load_sgm(infilepath)
               elif informat == self.SGML_FORMAT:
                   sgmdoc.load_sgml(infilepath)
               outfilename = filename.replace("."+informat, "."+outformat)
               outfilepath = os.path.join(outfolder, outfilename)
               if outformat == self.SGML_FORMAT:
                   sgmdoc.save_sgml(outfilepath)
               elif outformat == self.TXT_FORMAT:
                   sgmdoc.save_txt(outfilepath)






if __name__ == "__main__":
    infolder = "../../data/reuters21578/"
    outfolder = "./data/"
    converter = ReuterDSConverter(infolder, outfolder)
    converter.convert(ReuterDSConverter.SGM_FORMAT, 
        ReuterDSConverter.TXT_FORMAT)

    

