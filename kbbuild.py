from lang import LangModel


class EntityIdentifier:

    def __init__(self):
        self.organizations = []
        self.people = []
        self.places = []

    def identity_ents(self, text):
        nlp = LangModel.get_instance()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                self.organizations.append(ent.text)
            elif ent.label_ == 'PERSON':
                self.people.append(ent.text)
            elif ent.label_ == 'GPE':
                self.places.append(ent.text)

    def save_ents(self):
        with open('./data/orgs.txt', 'w') as orgfile:
            for org in self.organizations:
                orgfile.write(org + '\n')
        with open('./data/people.txt', 'w') as peoplefile:
            for person in self.people:
                peoplefile.write(person + '\n')
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