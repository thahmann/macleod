"""
Top level container for an ontology parsed into the object structure
"""

import os
import macleod.logical.Axiom as Axiom

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

    def resolve_imports(self, resolve=False):
        """
        Look over our list of imports and tokenize / parse any that haven't
        already been parsed
        """

        # Cyclic imports are kind of painful in Python
        import macleod.parsing.Parser as Parser

        # TODO: All that stuff about handling duplicate imports...
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
        / parsing for later

        :param String path, path to a referenced .clif file
        :return None
        """

        self.imports[path] = None

    def __repr__(self):
        """
        Nice printable output for the ontology
        """

        rep = ""
        rep += self.name
        rep += "\n"

        rep += '++++++++++++++++++++++++++++'
        for key in self.imports:
            rep += "\n" + key
        rep += '\n'
        rep += '----------------------------'

        rep += "\n"

        for axiom in self.axioms:
            rep += "\n" + repr(axiom)

        rep += "\n____________ Listing Resolved Imports of {}____________".format(self.name)
        for key in self.imports:
            rep += "\n" + repr(self.imports[key])
        rep += "\n_________________________________________________"

        return rep

            
