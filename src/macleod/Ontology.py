"""
Top level container for an ontology parsed into the object structure
"""


import logging
import os

import macleod.ReasonerSet
import macleod.dl.owl
import macleod.logical.axiom

import macleod.Filemgt
import macleod.Process
import macleod.dl.filters
import macleod.dl.translation


class Ontology(object):
    """
    The object to rule them all
    """

    CONSISTENT = 1
    INCONSISTENT = -1
    PROOF = -1
    COUNTEREXAMPLE = 1
    UNKNOWN = 0
    CONTRADICTION = -100
    ERROR = -50

    imported = {}

    def __init__(self, name, basepath=None, resolve=False, preserve_conditionals = True):

        # The full path to the file
        self.name = os.path.abspath(name)

        # Important in order to not reuse the seen OWL patterns from a prior ontology
        macleod.dl.translation.reset_seen()

        # For the time being, just maintain a list of axioms
        self.axioms = []

        # for flexibility, maintain a separate list of conjectures
        self.conjectures = []

        # Imports we handle with a [path] : [ontologies] dict
        self.imports = {}

        # Dict with [URI] : [filepath] to serve as the substitution string
        if basepath is None:
            self.basepath = macleod.Filemgt.get_ontology_basepath()
        else:
            self.basepath = basepath
        #logging.getLogger(__name__).info('Using URI ' + self.basepath[0] + ' to substitute for path ' + self.basepath[1])

        self.resolve = resolve

        # for keeping track of the terminology
        self.unary_predicates = set()
        self.binary_predicates = set()
        self.nary_predicates = set()
        self.all_predicates = set()
        self.consts = set()
        self.functs = set()
        # same for the terminology in the resulting OWL conversion
        self.classes = set()
        self.properties = set()
        self.pcnf_sentences = 0
        self.filtered_patterns = 0
        self.owl_axioms = 0

        self.transitive_extractions = []


        self.tptp_output = None
        self.tptp_file = None
        self.ladr_output = None
        self.ladr_file = None
        self.latex_output = None
        self.latex_file = None
        self.owl = None

        # store whether existential axioms for nontrivial consistency are added;
        # need to write output to different files then
        self.nontrivial = False

        # global variable to keep track of whether to preserve or eliminate conditionals
        # (applies to all subsequent instantiations of Ontology as well, when imports are processed)
        global conditionals
        conditionals = preserve_conditionals

        # enumerator for creating unique constants
        global var_enum
        var_enum = 0

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
        return self.axioms

    def resolve_imports(self):
        """
        Look over our list of imports and tokenize and parse any that haven't
        already been parsed;
        Calling this method also sets self.resolve to True (which is False by default)
        """

        self.resolve = True

        logging.getLogger(__name__).debug("Resolving imports")

        # Cyclic imports are kind of painful in Python
        import macleod.parsing.parser as Parser

        for path in self.imports:

            logging.getLogger(__name__).debug("Working on import " + path)

            if self.imports[path] is None:

                if path in Ontology.imported:
                    print("Cyclic import found: {} imports {}".format(self.name, path))
                    self.imports[path] = Ontology.imported[path]
                else:
                    sub, base = self.basepath
                    subbed_path = path.replace(self.basepath[0], self.basepath[1])
                    logging.getLogger(__name__).debug("Subbed path for import " + path)
                    # Need to immediately keep track of the ontology path in processing to not visit it again
                    # we later update the value with the actual created ontology object
                    Ontology.imported[path] = None
                    try:
                        logging.getLogger(__name__).info("Starting to parse " + subbed_path)
                        new_ontology = Parser.parse_file(subbed_path, sub, base, self.resolve, preserve_conditionals=conditionals)
                    except TypeError as e:
                        logging.getLogger(__name__).error("Error parsing " + subbed_path + ": " + str(e))

                    new_ontology.basepath = self.basepath
                    self.imports[path] = new_ontology
                    # update the import information with the created ontology object
                    Ontology.imported[path] = new_ontology

    def get_all_modules(self):
        """Get a flattened list of all Ontologies that are imported either directly or indirectly """

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
        of it and stores it in this ontology

        :param Logical logical, a parsed logical object
        :return None
        """

        self.axioms.append(macleod.logical.axiom.Axiom(logical))

    def add_conjecture(self, logical):
        """
        Accepts a logical object and creates an accompanying Axiom object out
        of it

        :param Logical logical, a parsed logical object
        :return None
        """

        self.conjecture.append(macleod.logical.axiom.Axiom(logical))

    def add_import(self, path):
        """
        Accepts a path to another .clif file in this case we defer tokenization
        and parsing for later

        :param String path, path to a referenced .clif file
        :return None
        """

        self.imports[path] = None

    def analyze_ontology(self):
        """
        Analyzes all axioms of the ontology and stores lists of predicates, etc.

        :return:
        """

        class WrappedSymbol(object):
            """
            Wrapping predicates and function symbols in a new class to make comparing, merging, etc. easier
            """
            def __init__(self, symbol):
                self.symbol = symbol

            def __eq__(self, other):
                # special treatment if either one is a string -- applies to constants only
                if isinstance(self.symbol, str) and isinstance(other.symbol, str):
                    return self.symbol==other.symbol
                elif isinstance(self.symbol, str) and not isinstance(other.symbol, str):
                    return self.symbol==other.symbol.name
                elif not isinstance(self.symbol, str) and isinstance(other.symbol, str):
                    return self.symbol.name == other.symbol
                else:
                    return self.symbol.same_symbol(other.symbol)

            def __hash__(self):
                if isinstance(self.symbol, str):
                    return hash(self.symbol)
                else:
                    return hash(self.symbol.name)

            def __repr__(self):
                if isinstance(self.symbol, str):
                    return self.symbol + "(0)"
                else:
                    return self.symbol.name + "(" + str(len(self.symbol.variables)) + ")"

        axioms = self.get_all_axioms()

        from macleod.logical.symbol import Function
        self.binary_predicates.add(WrappedSymbol(Function("=",["x","y"])))

        for (axiom, _) in axioms:
            # Aready done during axiom creation
            #axiom.analyze_logical()

            self.unary_predicates.update(set(WrappedSymbol(p) for p in axiom.unary_predicates))
            self.binary_predicates.update(set(WrappedSymbol(p) for p in axiom.binary_predicates))

            self.nary_predicates.update(set(WrappedSymbol(p) for p in axiom.nary_predicates))
            self.consts.update(set(WrappedSymbol(p) for p in axiom.consts))
            self.functs.update(set(WrappedSymbol(p) for p in axiom.functs))

        logging.getLogger(__name__).info("Unary predicates: {}".format(", ".join([repr(p) for p in self.unary_predicates])))
        logging.getLogger(__name__).info("Binary predicates: {}".format(", ".join([repr(p) for p in self.binary_predicates])))
        logging.getLogger(__name__).info("N-ary predicates: {}".format(", ".join([repr(p) for p in self.nary_predicates])))
        logging.getLogger(__name__).info("Functions: {}".format(", ".join([repr(p) for p in self.functs])))
        logging.getLogger(__name__).info("Constants: {}".format(", ".join([repr(p) for p in self.consts])))

        self.all_predicates = self.unary_predicates.union(self.binary_predicates).union(self.nary_predicates)

        # do some sanity checks
        # need to compare names; identity alone doesn't work
        intersection = self.unary_predicates & self.binary_predicates
        if bool(intersection):
            full_intersection = self.unary_predicates.intersection(self.binary_predicates)
            for i in full_intersection:
                logging.getLogger(__name__).warning("Predicate " + repr(i.symbol.name) + " used as unary predicate (class) and binary predicate (relation)")

        intersection = self.unary_predicates & self.nary_predicates
        if bool(intersection):
            full_intersection = self.unary_predicates.intersection(self.nary_predicates)
            for i in full_intersection:
                logging.getLogger(__name__).warning("Predicate " + repr(i.symbol.name) + " used as unary predicate (class) and n-ary predicate (relation)")

        intersection = self.binary_predicates & self.nary_predicates
        if bool(intersection):
            full_intersection = self.binary_predicates.intersection(self.nary_predicates)
            for i in full_intersection:
                logging.getLogger(__name__).warning("Predicate " + repr(i.symbol.name) + " used as binary and n-ary predicate (relation)")

        intersection = self.all_predicates & self.functs
        if bool(intersection):
            full_intersection = self.all_predicates.intersection(self.functs)
            for i in full_intersection:
                logging.getLogger(__name__).warning(repr(i.symbol.name) + " used as predicate and function symbol")

        #predicate_names = set([p.symbol.name for p in self.all_predicates])
        #function_names = set([p.symbol.name for p in self.functs])

        intersection = self.all_predicates & self.consts
        if bool(intersection):
            full_intersection = self.all_predicates.intersection(self.consts)
            for i in full_intersection:
                logging.getLogger(__name__).warning(i.symbol + " used as predicate and constant")

        intersection = self.functs & self.consts
        if bool(intersection):
            full_intersection = self.functs.intersection(self.consts)
            for i in full_intersection:
                logging.getLogger(__name__).warning(i.symbol + " used as function symbol and constant")

        # TODO comparing against constants needs to be done differently because they are just strings
        #intersection = self.consts & all_predicates
        #if bool(intersection):
        #    logging.getLogger(__name__).warning(intersection + " used as predicate and a constant")
        #intersection = self.consts & self.functs
        #if bool(intersection):
        #    logging.getLogger(__name__).warning(intersection + " used as a function symbol and a constant")

    def get_explicit_definitions(self):
        """
        Gets all explicit definitions form this ontology;
        need to make sure to call resolve_imports() first if all imported axioms should be included
        :return:
        """
        axioms = self.get_all_axioms()

        logging.getLogger(__name__).info("Looking for explicit definitions among " + str(len(axioms)) + " axioms")
        definitions = []
        for (axiom, _) in axioms:
            defined_term = axiom.is_explicit_definition()
            if defined_term is not False:
                definitions.append(axiom)
                logging.getLogger(__name__).info("Found explicitly defined predicate " + repr(defined_term) + " in axiom " + repr(axiom))

    def add_nontrivial_axioms(self):
        """
        Creates existentially quantified axioms that ascertain the satisfiability of each predicate

        :return:
        """

        axioms = self.get_all_axioms()

        self.analyze_ontology()

        logging.getLogger(__name__).info("Creating existential axioms to enforce nontrivial consistency")

        for pred in self.all_predicates:
            if pred.symbol.name=="=":
                # skip the equality predicate
                continue
            else:
                self.add_predicate_satisfiability_axiom(pred.symbol,True)
                self.add_predicate_satisfiability_axiom(pred.symbol,False)

        # Remember that nontrivial axioms have been created
        self.nontrivial = True


    def add_predicate_satisfiability_axiom(self, symbol, positive_polarity=True):
        """
        Creates and adds an axiom that ascertains the existence of a predicate
        (i.e. class, binary relation or n-ary predicate)
        :param symbol:
        :return:
        """

        from macleod.logical.symbol import (Function, Predicate)
        from macleod.logical.connective import Conjunction
        from macleod.logical.quantifier import Existential
        from macleod.logical.negation import Negation
        from macleod.logical.axiom import Axiom

        global var_enum

        arity = len(symbol.variables)
        # Create new constants for each variable
        vars = []
        for v in symbol.variables:
            var_enum += 1
            vars.append("var" + str(var_enum))

        atomic_term = Predicate(symbol.name, vars)
        if not positive_polarity:
            atomic_term = Negation(atomic_term)
        terms = [atomic_term]

        # create set of disjointness constraints
        for i in range(0,len(vars)):
            for j in range(i+1,len(vars)):
                var_pair = [vars[i],vars[j]]
                disjointness_term = Negation(Predicate("=",var_pair))
                terms.append(disjointness_term)

        conjunction = Conjunction(terms)
        axiom = Axiom(Existential(vars,conjunction))
        self.axioms.append(axiom)

    def to_tptp(self):
        """
        Translates all axioms in the module and, if present, in any imported modules to the TPTP format
        :return: TPTP conversions as a list of strings
        """
        if self.tptp_output is None:
            tptp_output = []

            for (axiom, path) in self.get_all_axioms():
                tptp_output.append(axiom.to_tptp())

            self.tptp_output = tptp_output

        return self.tptp_output

    def to_ladr(self):
        """
        Translates all axioms in the module and, if present, in any imported modules to the LADR format supported by Prover9 and Mace4
        :return: LADR conversions as a list of strings
        """

        if self.ladr_output is None:
            ladr_output = []

            all_axioms = self.get_all_axioms()
            for (axiom, path) in all_axioms:
                ladr_output.append(axiom.to_ladr())

            self.ladr_output = ladr_output

        return self.ladr_output

    def to_latex(self):
        """
        Translates all axioms in the module and, if present, in any imported modules to a LaTeX representation
        """

        if self.latex_output is None:
            latex_output = []

            all_axioms = self.get_all_axioms()
            for (axiom, path) in all_axioms:
                latex_output.append("$" + axiom.to_latex() +"$")

            self.latex_output = latex_output

        return self.latex_output

    def get_output_filename(self, output_type, out=False):
        # the following assumes that the names of the configuration sections
        # are the same as the names of the output (tptp/ladr/owl)
        ending = ""

        module_name = self.name.rsplit('.', 1)[0]

        if self.nontrivial:
            # attach something before the ending if the output is for a nontrivial consistency check
            module_name += "_nontrivial"

        if self.resolve:
            ending += macleod.Filemgt.read_config('output', 'all_ending')

        ending += macleod.Filemgt.read_config(output_type, 'ending')

        if out:
            ending += macleod.Filemgt.read_config("output", 'ending')
            folder_name = macleod.Filemgt.read_config("output", 'folder')
        else:
            folder_name = macleod.Filemgt.read_config(output_type, 'folder')

        output_filename = macleod.Filemgt.get_full_path(module_name,
                                                folder=folder_name,
                                                ending=ending)

        #print("OUTPUT FILE TO BE WRITTEN TO: " + str(output_filename))
        return output_filename

    def write_owl_file(self):

        logging.getLogger(__name__).info("Approximating " + self.name + " as an OWL ontology")

        #self.to_owl()

        profile_name = self.owl.get_profile_string()
        output_filename = self.get_output_filename(profile_name)

        with open(output_filename, "w") as f:
            f.write(self.owl.tostring(pretty_print=True))
        f.close()

        return output_filename


    def write_tptp_file(self):

        if self.tptp_file is None:
            logging.getLogger(__name__).info("Converting " + self.name + " to TPTP format")

            results = self.to_tptp()

            output_filename = self.get_output_filename('tptp')

            with open(output_filename, "w") as f:
                for sentence in results:
                    #print(sentence)
                    f.write(sentence + "\n")
                f.close()

            # save results to prevent redo the TPTP conversion
            self.tptp_file = output_filename

        return self.tptp_file

    def write_ladr_file(self):

        if self.ladr_file is None:
            logging.getLogger(__name__).info("Converting " + self.name + " to LADR format")

            results = self.to_ladr()

            output_filename = self.get_output_filename('ladr')

            with open(output_filename, "w") as f:
                if len(results) > 0:
                    f.write("formulas(sos).\n")
                    for sentence in results:
                        #print(sentence)
                        f.write(sentence + "\n")
                    f.write("end_of_list.\n")
                f.close()

            # save results to prevent redo the LADR conversion
            self.ladr_file = output_filename

        return self.ladr_file

    def write_latex_file(self, enumerate):

        if self.latex_file is None:
            logging.getLogger(__name__).info("Converting " + self.name + " to LaTeX format")

            results = self.to_latex()

            output_filename = self.get_output_filename('latex')

            with open(output_filename, "w") as f:
                f.write("\\documentclass{article}\n")

                f.write("\\usepackage{amsmath,amssymb,hyperref}\n\n")
                f.write("\\delimitershortfall = -0.5pt\n\n")

                printable_name = self.name.replace(os.sep, '/').replace("_", "\_")

                f.write("\\begin{document}\n")
                f.write("\\textbf{\\url{" + printable_name + "}}\n\n")
                if enumerate:
                    f.write("\\begin{enumerate}\n")
                for sentence in results:
                    print(sentence)
                    if enumerate:
                        f.write("\\item " + sentence + "\n")
                    else:
                        f.write(sentence + "\n\n")
                if enumerate:
                    f.write("\\end{enumerate}\n")
                f.write("\\end{document}")
                f.close()

            self.latex_file = output_filename

        return self.latex_file

    def check_consistency (self, options_files = None):
        """ test the input for consistency by trying to find a model or an inconsistency."""
        # want to create a subfolder for the output files

        reasoners = macleod.ReasonerSet.ReasonerSet()
        reasoners.constructAllCommands(self)
        logging.getLogger(__name__).info("USING " + str(len(reasoners)) + " REASONERS: " + str([r.name for r in reasoners]))

        # run provers and modelfinders simultaneously and wait until one returns
        reasoners = macleod.Process.raceProcesses(reasoners)

        # this captures our return code (consistent/inconsistent/unknown), not the reasoning processes return code
        (return_value, fastest_reasoner) = self.consolidate_results(reasoners)

        return (return_value, fastest_reasoner)

    # def prove_conjectures (self, resolve = True, options_files = None):
    #     """ try to prove each of the conjectures from the axioms with or without imported axioms."""
    #
    #     (return_value, reasoner) check_consistency(self,resolve, options_files)
    #     if return_value != CONSISTENT:
    #         return return_value
    #     else:
    #         # construct commands for each theorem
    #         for conjecture in self.conjectures:
    #             reasoners = ReasonerSet()
    #             reasoners.constructAllCommands(self,theorem)



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
                if return_value == Ontology.ERROR:
                    # Another prover found an error (likely syntax error), thus the result is not meaningful
                   continue
                if return_value == Ontology.UNKNOWN:
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
                    return_value = Ontology.CONTRADICTION
                    #print "CONTRADICTION: " + str(return_value)
                    logging.getLogger(__name__).warning("CONTRADICTORY RESULTS from " + self.name +': ' + r.name + ' and ' + successful_reasoner + ' disagree')
            if r.terminatedUnknowingly():
                logging.getLogger(__name__).info("UNKNOWN RESULT (" + str(r.output) + "): " + r.name)

        logging.getLogger(__name__).info("CONSOLIDATED RESULT: " + str(return_value))
        return (return_value, fastest_reasoner)

    def get_imported_axioms(self):
        """
        Traverses over all imports to create and return a list of all axioms found in the import closure.
        The axioms directly contained in the ontology are excluded from this list but can be accessed via self.axioms

        :return List imported_axioms, a list of tuples of the form (axiom, module name)
        """

        imported_axioms = []
        self.resolve_imports()

        seen_paths = []
        unprocessed = [x for x in self.imports.items()]
        while unprocessed:
            path, ontology = unprocessed.pop()
            if path not in seen_paths and ontology is not None:
                logging.getLogger(__name__).debug("Adding imported axioms from " + path)
                imported_axioms += [(a, path) for a in ontology.axioms]
                seen_paths.append(path)
                unprocessed += ontology.imports.items()

        logging.getLogger(__name__).info("Collected " + str(len(imported_axioms)) + " imported axioms")

        return imported_axioms

    def get_all_axioms(self):
        """
        Gets a list of all axioms found in the ontology itself and,
        if resolve is set (i.e. by calling resolve_imports()),
        also in its import closure

        :param resolve: Boolean that indicates whether to include all axioms from the import closure as well
        :return: axioms: list of all axioms (concatenation of axioms from the ontology and the imported axioms)
        """

        axioms = [(x, self.name) for x in self.axioms[:]]
        logging.getLogger(__name__).info("Found " + str(len(axioms)) + " axioms in " + self.name)

        if self.resolve:
            axioms +=self.get_imported_axioms()
            logging.getLogger(__name__).info("Working from a total of " + str(len(axioms)) + " axioms (including imported ones)")

        return axioms


    def to_owl(self, profile):
        """
        Return a string representation of this ontology in OWL format. If this ontology
        contains imports will translate those as well and concatenate all the axioms.

        :return String onto, this ontology in OWL format
        """

        import macleod.dl.patterns as Pattern

        if self.owl is None:

            # Create new OWL ontology instance
            # need to use normalized path to work properly on Windows
            onto = macleod.dl.owl.Owl(self.name,
                       self.name.replace(os.path.normpath(self.basepath[1]), self.basepath[0]).replace('.clif', '.owl').replace(os.sep, '/'),
                                      profile)

            axioms = self.get_all_axioms()

            # keeping track of classes (unary predicates) and properties (binary predicates) encountered
            # to avoid redundant declarations
            # predicates with the same arity and name are assumed to be identical

            # Loop over each Axiom and filter applicable patterns
            for axiom, path in axioms:

                print('Axiom: {} from {}'.format(axiom, path))
                pcnf = axiom.ff_pcnf()
                print('FF-PCNF: {}'.format(pcnf))

                # for completeness: declare all unary predicates as classes
                for unary in axiom.unary():
                    if unary.name not in self.classes:
                        self.classes.add(unary.name)
                        onto.declare_class(unary.name)

                # for completeness: declare all binary predicates as object properties
                for binary in axiom.binary():
                    if binary.name not in self.properties:
                        self.properties.add(binary.name)
                        onto.declare_property(binary.name)

                pcnf_sentences = macleod.dl.translation.translate_owl(pcnf)

                # Temporarily save all extractions to better sort and filter them
                extractions = []

                for pruned in pcnf_sentences:

                    self.pcnf_sentences += 1

                    tmp_axiom = macleod.logical.axiom.Axiom(pruned)
                    pattern_set = macleod.dl.filters.filter_axiom(tmp_axiom)

                    self.filtered_patterns += len(pattern_set)

                    #Collector for extracted patterns
                    for pattern in pattern_set:

                        extraction = pattern(tmp_axiom)
                        if extraction is not None:
                            print('     - pattern', extraction[0])
                            if pattern==Pattern.transitive_relation:
                                self.transitive_extractions.append(extraction)
                            else:
                                extractions.append(extraction)

                # TODO: now produce all the extracted axioms
                for extraction in extractions:
                    if macleod.dl.translation.produce_construct(extraction, onto):
                        self.owl_axioms += 1


                for extra in pcnf.extra_sentences:
                    for extra_pruned in macleod.dl.translation.translate_owl(extra):
                        tmp_axiom = macleod.logical.axiom.Axiom(extra_pruned)
                        pattern_set = macleod.dl.filters.filter_axiom(tmp_axiom)

                        self.filtered_patterns += len(pattern_set)

                        #Collector for extracted patterns
                        for pattern in pattern_set:

                            extraction = pattern(tmp_axiom)
                            if extraction is not None:
                                print('     - (extra) pattern', extraction[0])
                                if macleod.dl.translation.produce_construct(extraction, onto):
                                    self.owl_axioms += 1

            for extraction in self.transitive_extractions:
                logging.getLogger(__name__).info("Processing all transitive properties last")
                if macleod.dl.translation.produce_construct(extraction, onto):
                    self.owl_axioms += 1

                print()

            # TODO: Find another way to do this instead of case by case
            # etree.ElementTree html encodes special characters. Protege does not like this.
            # return onto.tostring()

            # add specialized constructs: disjoint union and equivalent classes
            # these are inferred from existing constructs (subclass and pairwise disjoint classes)
            onto.infer_disjoint_classes()
            onto.infer_equivalent_classes()
            
            self.owl = onto

        return self.owl

    def pretty_print(self, pcnf=False, tptp=False):
        '''
        Utility function to nicely print out an ontology and linked imports.
        Optionally will transform any axioms to their function-free prenex conjunctive
        normal form (FF-PCNF).

        :param Ontology ontology, An ontology object representing the top level file
        :param Boolean pcnf, Flag to transform axioms to FF-PCNF form
        '''

        ontologies = set()
        ontologies.add(self.name)

        processing = [self]

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
