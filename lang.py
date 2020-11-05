import spacy


class LangModel:
    __instance = None

    @staticmethod
    def get_instance():
        if LangModel.__instance is None:
            LangModel()
        return LangModel.__instance


    def __init__(self):
        if LangModel.__instance is not None:
            raise Exception("Cannot instanciate another Language model")
        else:
            print('Loading spacy model')
            LangModel.__instance = spacy.load("en_core_web_sm")
            LangModel.__instance.max_length = 20000000