


class EntitieIdentifier:

    def __init__(self):
        self.organizations = []
        self.people = []
        self.places = []

    def identity_ents(self, text):

        pass


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