

class NodeType:
    ORG = "ORG"
    PERSON = "PERSON"
    PLACE = "GPE"
    Set = {"ORG", "PERSON", "GPE"}


class EdgeType:
    TRADE = "TRADE"
    OTHER = "OTHER"
    Set = {"TRADE", "OTHER"}


class Node:

    def __init__(self, ent_id, ent_type, ent_label):
        self.ent_id = ent_id
        self.ent_type = ent_type
        self.ent_label = ent_label 

    @staticmethod
    def color(ent_type):
        if ent_type == 'PERSON': return 'red'
        elif ent_type == 'ORG': return 'blue'
        elif ent_type == 'GPE': return 'green'
        else: return 'gray'
    
    def __str__(self):
        return str(self.__dict__)


class Edge:

    def __init__(self, ent1_id, ent2_id, rel_type, rel_label):
        self.ent1_id = ent1_id
        self.ent2_id = ent2_id
        self.rel_type = rel_type
        self.rel_label = rel_label

    def __str__(self):
        return str(self.__dict__)
