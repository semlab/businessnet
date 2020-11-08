from lang import LangModel


class NodeType:
    ORG = "ORG"
    PERSON = "PERSON"
    PLACE = "GPE"
    Set = {"ORG", "PERSON", "GPE"}


class EdgeType:
    TRADE = "TRADE"
    OTHER = "OTHER"
    Set = {"TRADE", "OTHER"}

class EntityIdentifier:

    def __init__(self):
        self.organizations = []
        self.people = []
        self.places = []

    def identity_ents(self, text):
        nlp = LangModel.get_instance()
        doc = nlp(text)
        orgs = []
        people = []
        places = []
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                orgs.append(ent.text)
            elif ent.label_ == 'PERSON':
                people.append(ent.text)
            elif ent.label_ == 'GPE':
                places.append(ent.text)
        orgs = list(set(orgs))
        people = list(set(people))
        places = list(set(places))
        self.organizations.extend(orgs)
        self.people.extend(people)
        self.places.extend(places)

    
    def remove_duplicate(self):
        self.organizations = list(set(self.organizations))
        self.people = list(set(self.people))
        self.places = list(set(self.places))


    def save_ents(self):
        print("saving {} orgs".format(len(self.organizations)))
        with open('./data/orgs.txt', 'w') as orgfile:
            for org in self.organizations:
                orgfile.write(org + '\n')
        print("saving {} persons".format(len(self.people),))
        with open('./data/people.txt', 'w') as peoplefile:
            for person in self.people:
                peoplefile.write(person + '\n')
        print("saving {} places".format(len(self.places)))
        with open('./data/places.txt', 'w') as placesfile:
            for place in self.places:
                placesfile.write(place + '\n')



class EdgeBuilder:
    """
    Build relationships from OpenIE output
    """

    def __init__(self):
        self.triplets = []


    def edges_build(self, inputpath):
        edges = []
        lines = []
        with open(inputpath, 'r') as inputfile:
            lines = inputfile.readlines()
        line_iter = 0
        lines_count = len(line_iter)
        while line_iter < lines_count:
            sent_txt = lines[line_iter]
            line_iter += 1
            sent_extracts = []
            while line_iter < lines_count and lines[line_iter] != "":
                if re.match(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$", extraction) is not None:
                    sent_extracts.append(lines[line_iter])
                line_iter += 1
            edges.extend(sent_edges_build(sent_txt, sent_extracts))
        return edges


    def sent_edges_build(self, sent_txt, extractions):
        edges = []
        nlp = LangModel.get_instance()
        doc  = nlp(sent_txt)
        ents = [e for e in sent.ents if e.label_ in ents_filter
            for sent in doc.sents ]
        if len(ents) < 2:
            return edges
        for extraction in extractions:
            if re.match(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$", extraction):
                extract_str = extraction[4:-1]
                extract_parts = extract_str.split(';')
                ent1 = None
                ent2 = None
                rel = None
                for ent in ents:
                    if ent in extract_parts[0]:
                        #TODO: retrieve unique id of ent
                        ent1 = ent
                    elif ent in extract_parts[2]:
                        #TODO: retrieve unique id of ent
                        ent2 = ent
                #TODO: Retrieve edge type trade/other id
                rel = EdgeType.OTHER
                if ent1 is not None and ent2 is not None and rel is not None:
                    edges.append([ent1, rel, ent2])
        return edges



    def triplets_filter(self, inputfilepath, outputfilepath):
        """
        Filter OpenIE output file to keep
        interesting triplets
        """
        triplet_file_content = ""
        with open(inputfilepath, 'r') as inputfile:
            triplet_file_content = inputfile.read()
        triplets = re.findall(r"^[0-9]\.[0-9]{2} \(.*;.*;.*\)$", triplet_file_content)
        for idx, triplet in triplets:
            pass
        pass


if __name__ == "__main__":
    identifier = EntityIdentifier()
    sents_count = 0
    with open('./data/reuter_sentences.txt', 'r') as textfile:
        text = textfile.readline()
        while text :
            sents_count = sents_count + 1
            identifier.identity_ents(text) 
            text = textfile.readline()
            print(f'\r{sents_count} sentences processed', end='')
    print()
    identifier.remove_duplicate()
    identifier.save_ents()
