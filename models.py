

class NamedEntity:
    entid = None
    name = None
    aliases = []
    embedding = None



class Organisation(NamedEntity):
    pass

class Person(NamedEntity):
    pass

class Place(NamedEntity):
    pass 