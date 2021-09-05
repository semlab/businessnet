#!/usr/bin/python3

import os
import re
import spacy 
import xml.etree.ElementTree as ET
from io import StringIO

from lang import LangModel
from utils import printProgressBar
from models import NodeType




class CorpusPreproc:

    def __init__(self, location, outfilepath="out.txt"):
        self.location = location # location of the corpus (folder/file)
        self.outfilepath = outfilepath
        self.processedtext = ""
        pass

    
    def formattext(self, save=True):
        """
        Removes unecessary content to keep plain text from the file.
        """
        raise NotImplementedError()


    #def filter_sents(self, lang_proc):
    def filter_sents(self, text):
        """
        Keep sentences containing more than one named entities 
        (Organisation, Person, Location) names, one per line.
        sentence to be filtered are took from the self.processedtext member
        lang_proc: language processor (initialized with spacy.load(<model>))
        returns a list of filtrered sentences.
        """
        #doc = lang_proc(self.processedtext)
        #doc = lang_proc(text)
        nlp = LangModel.get_instance()
        doc = nlp(text)
        #ents_filter = ['ORG', 'PERSON', 'GPE'] # TODO: centralize
        filtered_sents = []
        #sents_count = len(doc.sents)
        #print("{} Sentences identified".format(sents_count))
        for idx, sent in enumerate(doc.sents):
            filtered_ents = [e for e in sent.ents if e.label_ in NodeType.Set]
            if (len(filtered_ents) > 1):
                filtered_sents.append(sent.string.strip())
        filtered_text = '\n'.join(filtered_sents)
        return filtered_text
            #printProgressBar(idx+1, sents_count)
        #self.processedtext = '\n'.join(filter_sents)
        #return self.processedtext



    def savetext(self, filemode='w'):
        with open(self.outfilepath, filemode) as outfile:
            outfile.write(self.processedtext)




class ReuterPreproc(CorpusPreproc):

    def formattext(self):
        #from cStringIO import StringIO
        content_filepaths = [ os.path.join(root, name)
            for root, dirs, files in os.walk(self.location)
            for name in files 
            if name.endswith(".sgm") ]
        processedtext = StringIO() 
        file_count = len(content_filepaths)
        for idx, content_filepath in enumerate(content_filepaths):
            text = self.read_reuterfile(content_filepath)
            text = self.format_articles(text, idx, file_count)
            text = self.filter_sents(text)
            processedtext.write(text)
        self.processedtext = processedtext.getvalue()
        return self.processedtext

    
    def formattext_files(self):
        content_filepaths = [os.path.join(root, name)
            for root, dirs, files in os.walk(self.location)
            for name in files
            if name.endswith(".sgm")]
        file_count = len(content_filepaths)
        for idx, content_filepath in enumerate(content_filepaths):
            text = self.read_reuterfile(content_filepath)
            text = self.format_articles(text, idx, file_count)
            text = self.filter_sents(text)
            folder, filename = os.path.split(content_filepath) 
            if not os.path.isdir(outfilepath): 
                i = 1
                while os.path.isfile(outfilepath + str(i)):
                    i += 1
                outfilepath = outfilepath + str(i)
                os.mkdir(outfilepath)
            filename = os.join(outfilepath,  filename + '.txt')
            with open(filename, 'w') as outfile:
                outfile.write(text)




    def read_reuterfile(self, file_path=None):
        if file_path == None: 
            return None
        file_content = None
        with open(file_path, 'r') as datafile:
            try: 
                file_content = datafile.read()
            except UnicodeDecodeError :
                #TODO: use logging
                print("WARNING: Error Decoding {}, file skipped".format(
                    file_path))
                file_content = None
        if file_content == None: 
            return None
        return file_content
        

    def format_articles(self, file_content, file_index=0, file_count=0, verbose=True):
        """
        @params:
            file_content    - Required: file content to be formatted
            file_index      - Optional: index of the current reuter articles file
            file_count      - Optional: total number of files to be formatted
        """
        if file_content is None or file_content == "":
            return ""
        progress_prefix="File {}/{}, art. {}/{}"
        article_contents = re.findall(r'<BODY>[\s\S]*?</BODY>', file_content)
        article_count = len(article_contents)
        for idx, article_content in enumerate(article_contents):
            article_content = article_content.replace(".\n", ".<br/>")
            article_content = article_content.replace(" Reuter\n", "")
            article_content = article_content.replace("<BODY>",  "\n")
            article_content = article_content.replace("&#3;</BODY>",  "\n\n")
            article_content = article_content.replace("&lt;", "<")
            article_content = article_content.replace("\n", " ")
            article_content = article_content.replace( ".<br/>", ".\n")
            #article_content = article_content.replace("<", "")
            #article_content = article_content.replace(">", "")
            article_contents[idx] = article_content
            # TODO: prepare cleaner content (remove tables and other non 
            # sentence  content.)
            if verbose:
                printProgressBar(file_index+1, 
                    file_count +1, 
                    prefix=progress_prefix.format(
                        file_index + (idx // article_count),
                        file_count,
                        idx+1,
                        article_count
                    )) 
        file_content = '\n'.join(article_contents)    
        return file_content



#class ReuterSGMLPreproc(CorpusPreproc):
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
        Using [[stockabbr]] to enclose non tag content like stocks name
        """
        # &lt;NAME>  -> [[NAME]]
        # abbr is the stock abbreviation
        formatted_text = ReuterSGMDoc.P_STOCKID.sub(r'[[\g<abbr>]]', 
                text)
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


    def save_sgml(self, filepath):
        if self.sgml is None:
            self.to_sgml()
        with open(filepath, 'w') as f:
            if self.sgml is not None:
                f.write(self.sgml)


    def save_txt(self, filepath):
        if self.txt is None:
            self.to_txt()
        with open(filepath, 'w') as f:
            if self.txt is not None:
                f.write(self.txt)


    def remove_tables(self, text):
        """Remove table from the text (plain text)"""
        return ReuterSGMDoc.P_TABLE.sub('\n', text)
        

    #def format_sgml(self, text):
    def to_sgml(self):
        # TODO change function name from to 'sgm_to_sgml'
        # TODO change 'text' variable name to 'sgm'
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


    #def sgml_to_text(self, sgml): 
    def to_txt(self): 
        """
        :param sgml: xml friendly formatted sgm file content
        :type sgml: str
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
            text = self.align_sents(text)
            text_content.append(text)
        self.txt =  "\n\n".join(text_content)
        return self.txt



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

    # TODO set it outside the object on its own
    #def format_dataset(self):
    #def sgm_to_sgml(self):
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
    #datafolder = "../../data"
    #local_datafolder= "data"
    #nlp = LangModel.get_instance()

    #reuter_folder = "{}/reuters21578-mld/reuters21578/".format(datafolder)
    #preproc = ReuterPreproc(reuter_folder, 
    #        outfilepath="{}/reuter_sentences.txt".format(local_datafolder))
    #print('formatting text...')
    #preproc.formattext()
    #preproc.savetext()

    # TODO save sgml as temp files
    #sgml_content = ""
    #with open("../../data/reuters21578/reuters21578/reut2-010.sgm") as f:
    #with open("../../data/reuters21578/reut2-010.sgm") as f:
    #    sgml_content = f.read()

    infolder = "../../data/reuters21578/"
    outfolder = "./data/"

    converter = ReuterDSConverter(infolder, outfolder)
    converter.convert(ReuterDSConverter.SGM_FORMAT, 
        ReuterDSConverter.TXT_FORMAT)

    #pp = ReuterSGMLPreproc()
    #pp.format_dataset(infolder, outfolder)
    #sgml_content = pp.format_stockid(sgml_content)
    #sgml_content = pp.format_sgml(sgml_content)
    #text = pp.sgml_to_text(sgml_content)
    #print(text)
