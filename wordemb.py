import os
from gensim.models import Word2Vec
from preproc import ReuterSGMDoc, ReuterDSConverter
from lang import LangModel


class SentenceIterator:

    def __init__(self, infolder):
        self.infolder = infolder


    def __iter__(self):
        # TODO yield from saved tokens in file
        nlp = LangModel.get_instance()
        for filename in os.listdir(self.infolder):
            if filename.endswith("."+ReuterDSConverter.TXT_FORMAT):
                text = ""
                with open(os.path.join(infolder, filename)) as f:
                    text = f.read()
                doc = nlp(text)
                for sent in doc.sents:
                    tokens = [tk.text.lower() for tk in sent if not 
                        tk.is_stop and tk.is_alpha and len(tk)>1] 
                    yield tokens


if __name__ == "__main__":
    infolder = "./data"
    outfilename = "reuter.w2v"
    sents = SentenceIterator(infolder)
    model = Word2Vec(sentences=sents, vector_size=100, window=5, 
        min_count=1, workers=4)
    model.save(outfilename)

