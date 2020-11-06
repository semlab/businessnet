from lang import LangModel


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



class OpenIELinker:
    """
    Build relationships from OpenIE output
    """

    def __init__(self):
        self.triplets = []


    def triplets_filter(inputfilepath, outputfilepath):
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
