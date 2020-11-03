import re
import spacy 



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
        for content_filepath in content_filepaths:
            text = __read_reuterfile(content_filepath)
            text = __reuter_formattext(text)
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
        

    def __reuter_formattext(self, file_content=None):
        article_contents = re.findall(r'<BODY>[\s\S]*?</BODY>', file_content)
        #article_contents = article_contents[3:4] #TODO: for testing to delete
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
        file_content = '\n'.join(article_contents)    
        return file_content



def gettext(file_path=None):
    """
    Removes unecessary content to keep plain text from the file.
    """
    if file_path == None: 
        return None
    file_content = None
    with open(file_path, 'r') as datafile:
        file_content = datafile.read()
    if file_content == None: 
        return None
    text_blocks = re.findall(r'<BODY>[\s\S]*?</BODY>', file_content)
    text = text_blocks[3] # Delete
    # Uncomment
    #text = '\n'.join(text_blocks)
    text = text.replace(".\n", ".<br/>")
    text = text.replace(" Reuter\n", "")
    text = text.replace("<BODY>",  "\n")
    text = text.replace("&#3;</BODY>",  "\n\n")
    text = text.replace("&lt;", "<")
    text = text.replace("\n", " ")
    text = text.replace( ".<br/>", ".\n")
    #text = text.replace("<", "")
    #text = text.replace(">", "")
    
    # TODO: prepare cleaner content (remove tables and other non sentence
    # content.)
    return text


def filter_sents(text, lang_proc):
    """
    Keep sentences containing more than one named entities 
    (Organisation, Person, Location) names, one per line.
    text : text containint sentences to be filtered.
    lang_proc: language processor (initialized with spacy.load(<model>))
    returns a list of filtrered sentences.
    """
    doc = lang_proc(text)
    ents_filter = ['ORG', 'PERSON', 'GPE']
    filtered_sents = []
    for sent in doc.sents:
        filtered_ents = [e for e in sent.ents if e.label_ in ents_filter]
        if (len(filtered_ents) > 1):
            filtered_sents.append(sent)
    return filtered_sents


def savetext(sentences, filepath):
    """
    Saves (append) a list of sentence to an outputfile 
    """
    sents_texts = [sent.string.strip()  for sent in sentences]
    text = '\n'.join(sents_texts)
    with open(filepath, 'a') as outputfile:
        outputfile.write(text)


def openie_triplet_filter(inputfilepath, outputfilepath):
    triplet_file_content = ""
    with open(inputfilepath, 'r') as inputfile:
        triplet_file_content = inputfile.read()
    triplets = re.findall(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$", triplet_file_content)
    for idx, triplet in triplets:
        pass
    pass


if __name__ == "__main__":
    datafolder = "../../data"
    local_datafolder= "data"
    model = "en_core_web_sm" # TODO: set it as console param
    nlp = spacy.load(model)
    reuter_file = "{}/reuters21578-mld/reuters21578/reut2-000.sgm".format(datafolder)
    

    #print('Getting text...')
    #text = gettext(reuter_file)
    #print('Filtering sentences...')
    #sents = filter_sents(text, nlp)
    #print("{} sentences extracted.".format(len(sents)))
    #print('Saving sentences...')
    #savetext(sents, "{}/reuter_sentences.txt".format(local_datafolder))
    #print('Done...')

    reuter_folder = "{}/reuters21578-mld/reuters21578/".format(datafolder)
    preproc = ReuterPreproc(reuter_folder, 
            outfilepath="{}/reuter_sentences.txt".format(local_datafolder))
    print('formatting text...')
    preproc.formattext()
    print('Filtering sentences...')
    preproc.filter_sents(nlp)
