"""
Top level container for an ontology parsed into the object structure
"""

import os
import owlready
import macleod.dl.OWL as Owl
import macleod.logical.Axiom as Axiom
import macleod.dl.Utilities as Util
import macleod.dl.Filters as Filter

def pretty_print(ontology, pcnf=False):
    '''
    Utility function to nicely print out an ontology and linked imports.
    Optionally will transform any axioms to their function-free prenex conjunctive 
    normal form (FF-PCNF).

    :param Ontology ontology, An ontology object representing the top level file
    :param Boolean pcnf, Flag to transform axioms to FF-PCNF form
    '''

    ontologies = set()
    ontologies.add(ontology.name)

    processing = [ontology]

    while processing != []:

        new = processing.pop()

        if new is not None:

            if pcnf:
                new.to_ffpcnf()

            for onto in new.imports.keys():

                if onto not in ontologies:
                    ontologies.add(onto)
                    processing.append(new.imports[onto])

            print(repr(new) + '\n')


class Ontology(object):
    """
    The object to rule them all
    """

    def __init__(self, name, basepath=None):

        # The full path to the file
        self.name = os.path.abspath(name)

        # For the time being, just maintain a list of axioms
        self.axioms = []

        # Imports we handle with a [path] : [ontologies] dict
        self.imports = {}

        # Dict with [URI] : [filepath] to serve as the substitution string
        self.basepath = basepath

    def to_ffpcnf(self):
        """
        Translate any held Axioms to their equivalent function-free prenex
        conjunctive normal form.

        :param self, Default for method
        :return None
        """

        temp_axioms = []

        for axiom in self.axioms:
            temp_axioms.append(axiom.ff_pcnf())

        self.axioms = temp_axioms

    def resolve_imports(self, resolve=False):
        """
        Look over our list of imports and tokenize and parse any that haven't
        already been parsed
        """

        # Cyclic imports are kind of painful in Python
        import macleod.parsing.Parser as Parser

        for path in self.imports:

            if self.imports[path] is None:

                sub, base = self.basepath
                subbed_path = path.replace(self.basepath[0], self.basepath[1])
                new_ontology = Parser.parse_file(subbed_path, sub, base, resolve)
                new_ontology.basepath = self.basepath
                self.imports[path] = new_ontology

    def add_axiom(self, logical):
        """
        Accepts a logical object and creates an accompanying Axiom object out
        of it

        :param Logical logical, a parsed logical object
        :return None
        """

        self.axioms.append(Axiom.Axiom(logical))

    def add_import(self, path):
        """
        Accepts a path to another .clif file in this case we defer tokenization
        and parsing for later

        :param String path, path to a referenced .clif file
        :return None
        """

        self.imports[path] = None

    def to_owl(self):
        """
        Return a string representation of this ontology in OWL format. If this ontology
        contains imports will translate those as well and concatenate all the axioms.

        :return String onto, this ontology in OWL format
        """

        # Create new OWL ontology instance
        onto = owlready.Ontology("http://junk/junk.owl")

        # Must convert to FF-PCNF first
        self.to_ffpcnf()

        # Loop over each Axiom and filter applicable patterns
        for axiom in self.axioms:

            pattern_set = Filter.filter_axiom(axiom)

            #Collector for extracted patterns
            for pattern in pattern_set:

                extraction = pattern(axiom)

                if extraction is not None:
                    Owl.produce_construct(extraction, onto)

        print(owlready.to_owl(onto))

    def __repr__(self):
        """
        Nice printable output for the ontology
        """

        rep = ""
        rep += '=' * (len(self.name) // 2 - 3) + ' NAME ' + '=' * (len(self.name) // 2 - 3) + '\n'
        rep += self.name + '\n'
        rep += '\n'

        rep += '-' * (len(self.name) // 2 - 4) + ' IMPORT ' + '-' * (len(self.name) // 2 - 4) + '\n'
        for key in self.imports:
            rep += key + '\n'
        rep += '\n'

        rep += '-' * (len(self.name) // 2 - 4) + ' AXIOMS ' + '-' * (len(self.name) // 2 - 4) + '\n'
        for axiom in self.axioms:
            rep += repr(axiom) + '\n'

        rep += '+' * len(self.name) + '\n'

        return rep
