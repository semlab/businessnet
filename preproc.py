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



class ReuterSGMLPreproc(CorpusPreproc):

    def __init__(self):
        pass

    def format_stock_abbr(self, text): 
        """
        Find and replace stock abbreviation enclosing 
        to avoid parsing error
        Using [[stockabbr]] to enclose non tag content like stocks name
        """
        # &lt;NAME>  -> [[NAME]]
        # abbr is the stock abbreviation
        p = re.compile('&lt;(?P<abbr>\w*)>')
        formatted_text = p.sub(r'[[\g<abbr>]]', text)
        return formatted_text

    def format_sgml(self, text):
        """Format the SGML file for better text manipulation"""
        # remove trailing 'Reuter' at the end of articles
        formatted_text = text.replace("Reuter\n&#3;</BODY>", "\n</BODY>")
        # remove unknown html entities
        p_htmlents = re.compile('&#[0-9]*;')
        formatted_text = p_htmlents.sub(r'', formatted_text)
        formatted_text = formatted_text.replace(
                '<!DOCTYPE lewis SYSTEM "lewis.dtd">',
                '<!DOCTYPE lewis SYSTEM "lewis.dtd">\n<SGML>')
        formatted_text = '\n'.join([formatted_text, "\n</SGML>"])
        return formatted_text

    def align_sents(self, text):
        """Put one sentence per line"""
        # TODO remove table first
        lines = text
        lines = lines.replace(".\n", ".<br/>")
        lines = lines.replace("\n", "")
        lines = lines.replace("<br/>", "\n")
        return lines


    def parse_sgml(self, sgml_content): 
        # TODO
        root = ET.fromstring(sgml_content)
        for body in root.iter("BODY"):
            print(body.text)
            lines = self.align_sents(body.text)
            print(lines)
            break




if __name__ == "__main__":
    datafolder = "../../data"
    local_datafolder= "data"
    nlp = LangModel.get_instance()

    #reuter_folder = "{}/reuters21578-mld/reuters21578/".format(datafolder)
    #preproc = ReuterPreproc(reuter_folder, 
    #        outfilepath="{}/reuter_sentences.txt".format(local_datafolder))
    #print('formatting text...')
    #preproc.formattext()
    #preproc.savetext()

    sgml_content = ""
    with open("../../data/reuters21578/reuters21578/reut2-010.sgm") as f:
        sgml_content = f.read()

    pp = ReuterSGMLPreproc()
    sgml_content = pp.format_stock_abbr(sgml_content)
    sgml_content = pp.format_sgml(sgml_content)
    pp.parse_sgml(sgml_content)
