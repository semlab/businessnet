import json

class NodeType:
    ORG = "ORG"
    PERSON = "PERSON"
    PLACE = "GPE"
    Set = ["ORG", "PERSON", "GPE"]


class EdgeType:
    TRADE = "TRADE"
    OTHER = "OTHER"
    Set = ["TRADE", "OTHER"]


class Node:
    """
    ent_count is the number of time the entity was identify in the corpus
    """

    def __init__(self, ent_id, ent_type, ent_label, ent_count=0):
        self.ent_id = ent_id
        self.ent_type = ent_type
        self.ent_label = ent_label 
        self.ent_count = ent_count

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


    @staticmethod
    def get_type(node1_type, node2_type):
        s = {node1_type, node2_type}
        if node1_type == node2_type:
            return 0
        elif s == {"ORG", "PEOPLE"}:
            return 1
        elif s == {"ORG", "GPE"}:
            return 2
        elif s == {"PEOPLE", "GPE"}:
            return 3
        else:
            return -1

    def __str__(self):
        return str(self.__dict__)


class NodeEncoder(json.JSONEncoder):

    def default(self, obj):
        if issinstance(obj, Node):
            return {
                'ent_id': obj.ent1_id,
                'ent_type': obj.ent_type,
                'ent_label': obj.ent_label
            }
        return json.JSONEncoder(self, obj)
