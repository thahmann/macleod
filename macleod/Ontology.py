"""
Top level container for an ontology parsed into the object structure
"""

import os

from macleod.dl.owl import Owl
from macleod.logical.axiom import Axiom
import macleod.dl.filters as Filter
import macleod.dl.translation as Translation
import macleod.dl.utilities as Util

def pretty_print(ontology, pcnf=False, tptp=False):
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

            for onto in new.imports.keys():
                if onto.name not in ontologies:
                    ontologies.add(onto.name)
                    processing.append(new.imports[onto])

            if pcnf:
                new.to_ffpcnf()

            print(repr(new) + '\n')


class Ontology(object):
    """
    The object to rule them all
    """

    imported = {}

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
            print(axiom)
            temp_axioms.append(axiom.ff_pcnf())

        self.axioms = temp_axioms
        print(self.axioms)

    def resolve_imports(self, resolve=False):
        """
        Look over our list of imports and tokenize and parse any that haven't
        already been parsed
        """

        # TODO: At some point need to do some kind of deduping on the import hierarchy 
        # to save on processing time. This may have an impact on translation later on
        import macleod.parsing.parser as Parser

        for path in self.imports:

            if self.imports[path] is None:

                if path in Ontology.imported:
                    print("Cyclic import found: {} imports {}".format(self.name, path))
                    self.imports[path] = Ontology.imported[path]
                else:
                    sub, base = self.basepath
                    subbed_path = path.replace(self.basepath[0], self.basepath[1])
                    new_ontology = Parser.parse_file(subbed_path, sub, base, resolve)
                    new_ontology.basepath = self.basepath
                    self.imports[path] = new_ontology
                    Ontology.imported[path] = new_ontology

    def add_axiom(self, logical):
        """
        Accepts a logical object and creates an accompanying Axiom object out
        of it and stores it in this ontology

        :param Logical logical, a parsed logical object
        :return None
        """

        self.axioms.append(Axiom(logical))

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
        onto = Owl(self.name.replace(self.basepath[1], self.basepath[0]).replace('.clif', '.owl'))

        # Create a nice long list of all axioms first
        seen_paths = []
        axioms = [(x, self.name) for x in self.axioms[:]]

        unprocessed = [x for x in self.imports.items()]
        while unprocessed:
            path, ontology = unprocessed.pop()
            if path not in seen_paths and ontology is not None:
                axioms += [(a, path) for a in ontology.axioms]
                seen_paths.append(path)
                unprocessed += ontology.imports.items()

        # Loop over each Axiom and filter applicable patterns
        for axiom, path in axioms:

            print('Axiom: {} from {}'.format(axiom, path))
            pcnf = axiom.ff_pcnf()
            print('FF-PCNF: {}'.format(pcnf))

            for pruned in Translation.translate_owl(pcnf):

                tmp_axiom = Axiom(pruned)
                pattern_set = Filter.filter_axiom(tmp_axiom)

                #Collector for extracted patterns
                for pattern in pattern_set:

                    extraction = pattern(tmp_axiom)
                    if extraction is not None:
                        print('     - pattern', extraction[0])
                        Translation.produce_construct(extraction, onto)

            for extra in pcnf.extra_sentences:
                for extra_pruned in Translation.translate_owl(extra):
                    tmp_axiom = Axiom(extra_pruned)
                    pattern_set = Filter.filter_axiom(tmp_axiom)

                    #Collector for extracted patterns
                    for pattern in pattern_set:

                        extraction = pattern(tmp_axiom)
                        if extraction is not None:
                            print('     - (extra) pattern', extraction[0])
                            Translation.produce_construct(extraction, onto)

            print()

        # TODO: Find another way to do this instead of case by case
        # etree.ElementTree html encodes special characters. Protege does not like this.
        return onto.tostring()

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
