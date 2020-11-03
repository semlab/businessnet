import re
import spacy 

from utils import printProgressBar



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


    def filter_sents(self, lang_proc):
        """
        Keep sentences containing more than one named entities 
        (Organisation, Person, Location) names, one per line.
        sentence to be filtered are took from the self.processedtext member
        lang_proc: language processor (initialized with spacy.load(<model>))
        returns a list of filtrered sentences.
        """
        doc = lang_proc(self.processedtext)
        ents_filter = ['ORG', 'PERSON', 'GPE']
        filtered_sents = []
        for sent in doc.sents:
            filtered_ents = [e for e in sent.ents if e.label_ in ents_filter]
            if (len(filtered_ents) > 1):
                filtered_sents.append(sent.string.strip())
        self.processedtext = '\n'.join(filter_sents)
        return self.processedtext


    def savetext(self, filemode='a'):
        with open(self.outfilepath, filemode) as outfile:
            outfile.write(text)



class ReuterPreproc(CorpusPreproc):

    def formattext(self):
        from cStringIO import StringIO
        content_filepaths = [ os.path.join(root, name)
            for root, dirs, files in os.walk(self.location)
            for name in files 
            if name.endwith(".sgm") ]
        processedtext = ""
        for idx, content_filepath in enumerate(content_filepaths):
            print("Formating file {}/{}".format(idx+1, len(content_filepaths)))
            text = __read_reuterfile(content_filepath)
            text = format_articles(text)
            processedtext.write(text)
        self.processedtext = processedtext.getvalue()
        return self.processedtext


    def __read_reuterfile(self, file_path=None):
        if file_path == None: 
            return None
        file_content = None
        with open(file_path, 'r') as datafile:
            file_content = datafile.read()
        if file_content == None: 
            return None
        return file_content
        

    def format_articles(self, file_content):
        article_contents = re.findall(r'<BODY>[\s\S]*?</BODY>', file_content)
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
            printProgressBar(idx+1, len(article_contents)) 
        file_content = '\n'.join(article_contents)    
        return file_content


if __name__ == "__main__":
    datafolder = "../../data"
    local_datafolder= "data"
    model = "en_core_web_sm" # TODO: set it as console param
    nlp = spacy.load(model)
    reuter_file = "{}/reuters21578-mld/reuters21578/reut2-000.sgm".format(datafolder)

    reuter_folder = "{}/reuters21578-mld/reuters21578/".format(datafolder)
    preproc = ReuterPreproc(reuter_folder, 
            outfilepath="{}/reuter_sentences.txt".format(local_datafolder))
    print('formatting text...')
    preproc.formattext()
    print('Filtering sentences...')
    preproc.filter_sents(nlp)
