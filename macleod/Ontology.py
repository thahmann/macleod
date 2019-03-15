"""
Top level container for an ontology parsed into the object structure
"""

import os

import logging

import macleod.logical.Axiom as Axiom
import macleod.Filemgt as Filemgt
import macleod.Process as Process
from macleod.ReasonerSet import *

CONSISTENT = 1
INCONSISTENT = -1
PROOF = -1
COUNTEREXAMPLE = 1
UNKNOWN = 0
CONTRADICTION = -100
ERROR = -50


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

        self.resolve = False


    def to_ffpcnf(self):
        """
        Translate any held Axioms to their equivalent function-free prenex
        conjunctive normal form.

        :param self, Default for method
        :return None
        """

        temp_axioms = []

        for axiom in self.axioms:
            temp_axioms.append(axiom.to_pcnf())

        self.axioms = temp_axioms

    def resolve_imports(self, resolve=False):
        """
        Look over our list of imports and tokenize / parse any that haven't
        already been parsed
        """
        self.resolve = resolve
        # Cyclic imports are kind of painful in Python
        import macleod.parsing.Parser as Parser

        for path in self.imports:

            if self.imports[path] is None:

                sub, base = self.basepath
                subbed_path = path.replace(self.basepath[0], self.basepath[1])
                subbed_path = os.path.normpath(subbed_path)
                new_ontology = Parser.parse_file(subbed_path, sub, base, resolve)
                new_ontology.basepath = self.basepath
                self.imports[path] = new_ontology

    def get_all_modules(self):
        """Get a flatten list of all Ontologies that are imported either directly or indirectly """

        all_modules=[self]
        all_modules_names = set()
        all_modules_names.add(self.name)

        processing = [self]

        while processing != []:

            new = processing.pop()
            print("Processsing " + new.name)

            if new is not None:

                for onto in new.imports.values():
                    print ("Found import " + onto.name)
                    if onto.name not in all_modules_names:
                        print("New import " + onto.name)
                        all_modules_names.add(onto.name)
                        all_modules.append(onto)
                        processing.append(onto)

            #print(len(all_modules_names))
            #print(len(all_modules))
        return all_modules


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
        
    def to_tptp(self, resolve=True):
        """
        Translates all axioms in the module and, if present, in any imported modules to the TPTP format
        """
        tptp_output = []

        if resolve:
            all_modules = self.get_all_modules()
        else:
            all_modules = [self]

        for module in all_modules:
            print("Processing " + module.name)
            for axiom in module.axioms:
                tptp_output.append(axiom.to_tptp())
                #print(axiom)

        return tptp_output



    def to_ladr(self, resolve=True):
        """
        Translates all axioms in the module and, if present, in any imported modules to the LADR format supported by Prover9 and Mace4
        """

        ladr_output = []

        if resolve:
            all_modules = self.get_all_modules()
        else:
            all_modules = [self]


        ladr_output.append('formulas(assumptions).')

        for module in all_modules:
            print("Processing " + module.name)
            for axiom in module.axioms:
                ladr_output.append(axiom.to_ladr())
                #print(axiom)

        ladr_output.append('end_of_list.\n')

        return ladr_output


    def check_consistency (self, resolve=True, options_files = None):
        """ test the input for consistency by trying to find a model or an inconsistency."""
        # want to create a subfolder for the output files

        reasoners = ReasonerSet()
        reasoners.constructAllCommands(self)
        logging.getLogger(__name__).info("USING " + str(len(reasoners)) + " REASONERS: " + str([r.name for r in reasoners]))

        # run provers and modelfinders simultaneously and wait until one returns
        reasoners = Process.raceProcesses(reasoners)

        # this captures our return code (consistent/inconsistent/unknown), not the reasoning processes return code
        (return_value, fastest_reasoner) = self.consolidate_results(reasoners)

        return (return_value, fastest_reasoner)


    def consolidate_results (self, reasoners):
        """ check all the return codes from the provers and model finders to find whether a model or inconsistency has been found.
        return values:
        consistent (1) -- model found, the ontology is consistent
        unknown (0) -- unknown result (no model and no inconsistency found)
        inconsistent (-1) -- an inconsistency has been found in the ontology
         """
        return_value = 0
        successful_reasoner = ''
        fastest_reasoner = None

        for r in reasoners:
            if r.terminatedWithError():
                return_value = r.output
                logging.getLogger(__name__).info("TERMINATED WITH ERROR (" + str(r.output) + "): " + r.name)
            if r.terminatedSuccessfully():
                if return_value == ERROR:
                    # Another prover found an error (likely syntax error), thus the result is not meaningful
                   continue
                if return_value == UNKNOWN:
                    return_value = r.output
                    logging.getLogger(__name__).info("TERMINATED SUCCESSFULLY (" + str(r.output) + "): " + r.name)
                    successful_reasoner = r.name
                    fastest_reasoner = r
                elif return_value == r.output:
                    logging.getLogger(__name__).info("TERMINATED SUCCESSFULLY (" + str(r.output) + "): " + r.name)
                    successful_reasoner += " " + r.name
                    if (r.time<fastest_reasoner.time):
                        fastest_reasoner = r
                elif return_value != r.output:
                    return_value = CONTRADICTION
                    #print "CONTRADICTION: " + str(return_value)
                    logging.getLogger(__name__).warning("CONTRADICTORY RESULTS from " + self.name +': ' + r.name + ' and ' + successful_reasoner + ' disagree')
            if r.terminatedUnknowingly():
                logging.getLogger(__name__).info("UNKNOWN RESULT (" + str(r.output) + "): " + r.name)

        logging.getLogger(__name__).info("CONSOLIDATED RESULT: " + str(return_value))
        return (return_value, fastest_reasoner)

    def __repr__(self):
        """
        Nice printable output for the ontology
        """

        rep = ""
        rep += '=' * (len(self.name) // 2 - 3) + ' NAME ' + '=' * (len(self.name) // 2 - 3) + '\n'
        rep += self.name + '\n'
        rep += '\n'

        rep += '+' * (len(self.name) // 2 - 4) + ' IMPORT ' + '+' * (len(self.name) // 2 - 4) + '\n'
        for key in self.imports:
            rep += key + '\n'
        rep += '\n'

        rep += '-' * (len(self.name) // 2 - 4) + ' AXIOMS ' + '-' * (len(self.name) // 2 - 4) + '\n'
        for axiom in self.axioms:
            rep += repr(axiom) + '\n'

        rep += '_' * len(self.name) + '\n'

        return rep

            
