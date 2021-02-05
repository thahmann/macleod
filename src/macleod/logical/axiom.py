"""
Axiom class
"""

import copy
import logging
import functools

from macleod.logical.logical import Logical
from macleod.logical.connective import (Conjunction, Disjunction, Connective, Conditional, Biconditional)
from macleod.logical.quantifier import (Universal, Existential, Quantifier)
from macleod.logical.negation import Negation
from macleod.logical.symbol import (Function, Predicate)
import macleod.logical.utils as Util

LOGGER = logging.getLogger(__name__)


class Axiom(object):
    """
    Used as a wrapper around individual sentences given in an ontology. Contains
    metrics on the sentence such as quantifier count, number of variables, type of
    predicates, etc. Also has utility methods to convert a sentence to FF-PCNF and
    potentially other formats.

    :param Logical sentence, a Logical object
    :return Axiom axiom
    """

    # Internal axiom counter for tptp and ladr translations
    axiom_id = 1

    def __init__(self, sentence):

        if not isinstance(sentence, Logical):
            raise ValueError("Axiom need Logicals")

        self.sentence = sentence
        self.extra_sentences = []

        self.unary_predicates = None
        self.binary_predicates = None
        self.nary_predicates = None
        self.negated_predicates = None
        self.positive_predicates = None
        self.uni_quantifiers = None
        self.uni_variables = None
        self.exi_quantifiers = None
        self.exi_variables = None
        self.consts = None

        self.id = Axiom.axiom_id
        Axiom.axiom_id = Axiom.axiom_id + 1

        # Build our cache of useful information
        # TODO: Figure out how to not make it crash rather than just comment this out
        self.analyze_logical()

    def quantifiers(self):
        """
        Returns a list of universal and existential quantifiers.

        :return List quantifiers, all the contained quantifiers
        """

        return self.uni_quantifiers + self.exi_quantifiers

    def universal_quantifiers(self):
        """
        Returns a list of universal quantifiers.

        :return List quantifiers, the universal quantifiers
        """

        return self.uni_quantifiers

    def existential_quantifiers(self):
        """
        Returns a list of existential quantifiers.

        :return List quantifiers, the existential quantifiers
        """

        return self.exi_quantifiers

    def variables(self):
        """
        Returns a list of all variables.

        :return List variables, list of strings
        """

        return self.uni_variables + self.exi_variables

    def universal_variables(self):
        """
        Returns a list of universal variables.

        :return List variables, list of strings
        """

        return self.uni_variables

    def existential_variables(self):
        """
        Returns a list of universal variables.

        :return List variables, list of strings
        """

        return self.uni_variables

    def predicates(self):
        """
        Returns a list of predicates.

        :return List predicates, list of predicates
        """

        return self.unary() + self.binary() + self.nary()

    def unary(self):
        """
        Returns a list of all unary predicates.

        :return List predicates, list of unary predicates
        """

        return self.unary_predicates

    def binary(self):
        """
        Returns a list of all binary predicates.

        :return List predicates, list of binary predicates
        """

        return self.binary_predicates

    def nary(self):
        """
        Returns a list of all nary predicates.

        :return List predicates, list of nary predicates
        """

        return self.nary_predicates

    def positive(self):
        """
        Returns a list of all non-negated predicates

        :return List predicates, list of non-negated predicates
        """

        return self.positive_predicates

    def negated(self):
        """
        Returns a list of all negated predicates

        :return List predicates, list of negated predicates
        """

        return self.negated_predicates

    def constants(self):
        """
        Returns a list of all constant/unquantified variabels that appear in
        the axiom.

        :return List constants, list of all constants
        """

        return self.consts

    def substitute_functions(self):
        """
        Recurse over the contained logical replacing any nested functions with
        new predicates.
        """

        functions = []
        ret_object = copy.deepcopy(self.sentence)
        axiom = Axiom(Util.dfs_functions(ret_object, functions, None))

        # Form explicit function declaration to keep tight logical equivalence
        declarations = []
        unique_functions = {f.name for f in functions if len(f.variables) == 2}

        for function in unique_functions:
            LOGGER.debug('Adding function declaration on: {}'.format(function))
            term_one = ~(Predicate(function, ['a', 'b']))
            term_two = ~(Predicate(function, ['a', 'c']))
            equality = Predicate('=', ['c', 'b'])
            sentence = Universal(['a', 'b', 'c'], term_one | term_two | equality)
            declarations.append(Axiom(sentence))

        return axiom, declarations

    def standardize_variables(self):
        """
        Recurse over the contained logical substituting all variables to ensure
        that only unique variables exist.
        """

        ret_object = copy.deepcopy(self.sentence)
        return Axiom(Util.dfs_standardize(ret_object, Util.generator(),))

    def push_negation(self):
        """
        Recurse over the logical pushing negation down to the predicate level.
        """

        ret_object = copy.deepcopy(self.sentence)
        return Axiom(Util.dfs_negate(ret_object))

    def create_prenex(self):
        """
        Recurse over the logical pulling quantifiers to the front.
        """

        # Acquire the starting Logical
        ret_obj = copy.deepcopy(self.sentence)

        # Build the reverse BFS queue
        queue = Util.reverse_bfs(ret_obj)

        # Traverse all the Logicals in reverse BFS order
        for term, parent in queue:

            LOGGER.debug("Term: " + repr(term))

            if isinstance(term, Connective):

                # Quantifier coalescence
                coalesced_term = term.coalesce()
                LOGGER.debug("Coalesced Term: " + repr(coalesced_term))

                if isinstance(coalesced_term, Connective):
                    scoped_term = coalesced_term.rescope(parent)
                    LOGGER.debug("Rescoped Term: " + repr(scoped_term))
                else:
                    scoped_term = coalesced_term


                if not parent is None:
                    # Nested within the BFS tree
                    parent.remove_term(term)
                    parent.set_term(scoped_term)

                else:
                    # Hit the top level Logical
                    ret_obj = scoped_term

        if isinstance(ret_obj, Quantifier):
            LOGGER.debug("Duplicated Prenex: " + repr(ret_obj))
            ret_obj = ret_obj.simplify()

        return Axiom(ret_obj)

    def distribute_disjunctions(self):
        """
        Recursively distribute disjunctions to form a valid conjunctive normal
        form Logical
        """

        ret_object = copy.deepcopy(self.sentence)
        return Axiom(ret_object.to_onf())

    def ff_pcnf(self):
        """
        Apply logical operations to translate the axiom into a function free
        prenex conjunctive normal form.
        """

        copied = copy.deepcopy(self)
        LOGGER.debug("Starting Axiom: " + repr(copied))

        function_free, declaration = copied.substitute_functions()
        LOGGER.debug("Function Free: " + repr(function_free))

        unique_variables = function_free.standardize_variables()
        LOGGER.debug("Unique Variables: " + repr(unique_variables))

        distributed_negation = unique_variables.push_negation()
        LOGGER.debug("Distributed Negation: " + repr(distributed_negation))

        prenex_form = distributed_negation.create_prenex()
        LOGGER.debug("Prenex Form: " + repr(prenex_form))

        cnf = prenex_form.distribute_disjunctions()
        LOGGER.debug("CNF Form: " + repr(cnf))

        #Add additional function declarations if they exist
        if declaration is not None:
            cnf.extra_sentences = declaration

        return cnf

    def analyze_logical(self):
        """
        Build a cache of useful information about the contained Logical.
        """

        def analyze_logical(term, accumulator, parent):
            """
            Utility function which searches a Logical and returns a tuple of
            lists with indexed data. Returns a list of universals,
            existentials, unary, binary, n-ary, negated, and non-negated
            predicates as well as any non-quantified variables (constants).

            :param Logical term, current item in the search
            :param Tuple accumulator, our tuple of lists
            :param Logical parent, parent of current DFS node
            :return None
            """

            if isinstance(term, Predicate) or isinstance(term, Function):

                # Don't count negations or binary, unary, n-ary with functions
                if not isinstance(term, Function):

                    if isinstance(parent, Negation):
                        accumulator[5].append(term)
                    else:
                        accumulator[6].append(term)

                    if len(term.variables) == 1:
                        accumulator[2].append(term)
                    elif len(term.variables) == 2:
                        accumulator[3].append(term)
                    else:
                        accumulator[4].append(term)

                for var in term.variables:

                    if isinstance(var, Function):
                        analyze_logical(var, accumulator, term)

                    else:
                        # TODO: Bug here if a constant with the same name as a variable appears
                        #       in a quantified + un-quantified portion of the same logical. Really
                        #       should never happen, but still will need to fix at some point.
                        if var not in accumulator[7] and var not in accumulator[8]:
                            accumulator[9].append(var)

            elif isinstance(term, Quantifier):

                if isinstance(term, Universal):
                    accumulator[0].append(term)
                    accumulator[7].extend(term.variables)
                else:
                    accumulator[1].append(term)
                    accumulator[8].extend(term.variables)

                _ = [analyze_logical(x, accumulator, term) for x in term.get_term()]

            else:

                _ = [analyze_logical(x, accumulator, term) for x in term.get_term()]

        analysis = [[], [], [], [], [], [], [], [], [], []]
        analyze_logical(self.sentence, analysis, None)

        self.uni_quantifiers = analysis[0]
        self.exi_quantifiers = analysis[1]
        self.unary_predicates = analysis[2]
        self.binary_predicates = analysis[3]
        self.nary_predicates = analysis[4]
        self.negated_predicates = analysis[5]
        self.positive_predicates = analysis[6]
        self.uni_variables = analysis[7]
        self.exi_variables = analysis[8]
        self.consts = analysis[9]

    def to_tptp(self):
        """
        Produce a TPTP representation of this axiom.

        :return str tptp, TPTP formatted version of this axiom
        """

        # For printing to TPTP add Axiom identifier to each variable to keep it unique
        variable_map = {}
        for var in self.variables():
            variable_map[var.upper()] = var.upper() + str(self.id)

        def tptp_logical(logical):
            """
            :param logical: term to be translated to TPTP
            :return: TPTP version of the logical term; variables are converted to upper case and predicates and functions to lower case
            """

            if isinstance(logical, str):
                return str.upper(logical)

            elif isinstance(logical, Predicate):
                if logical.is_equality():
                    return tptp_logical(logical.variables[0])  + logical.name + tptp_logical(logical.variables[1])
                else:
                    return "{}({})".format(str.lower(logical.name), ",".join([tptp_logical(t) for t in logical.variables]))

            elif isinstance(logical, Function):
                return "{}({})".format(str.lower(logical.name), ",".join([tptp_logical(t) for t in logical.variables]))

            elif isinstance(logical, Negation):
                if isinstance(logical.terms[0], Negation):
                    # get rid of double negation
                    return tptp_logical(logical.terms[0].terms[0])
                elif isinstance(logical.terms[0], Predicate):
                    # put parentheses around single predicates to not mix them up with special-symbol predicates
                    return "~({})".format(tptp_logical(logical.terms[0]))
                else:
                    return "~{}".format(tptp_logical(logical.terms[0]))

            elif isinstance(logical, Conjunction):
                return "({})".format(" & ".join([tptp_logical(t) for t in logical.terms]))

            elif isinstance(logical, Disjunction):
                return "({})".format(" | ".join([tptp_logical(t) for t in logical.terms]))

            elif isinstance(logical, Conditional):
                return "({} -> {})".format(logical.terms[0],logical.terms[1])

            elif isinstance(logical, Biconditional):
                return "({} <-> {})".format(logical.terms[0],logical.terms[1])

            elif isinstance(logical, Universal):
                return "({} ({}))".format(("! [{}] : " * len(logical.variables)).format(*[str.upper(var) for var in logical.variables]), tptp_logical(logical.terms[0]))

            elif isinstance(logical, Existential):
                return "({} ({}))".format(("? [{}] : " * len(logical.variables)).format(*[str.upper(var) for var in logical.variables]), tptp_logical(logical.terms[0]))

            else:
                raise ValueError("Not a valid type for TPTP output")

        return "fof(axiom{}, axiom, {}).".format(str(self.id*10),tptp_logical(self.sentence))


    def to_ladr(self):
        """
        Produce a LADR representation of this axiom.

        :return str ladr, LADR formatted version of this axiom
        """

        def ladr_logical(logical):

            if isinstance(logical, str):
                return logical
            elif isinstance(logical, Predicate):
                return "{}({})".format(logical.name, ",".join([ladr_logical(t) for t in logical.variables]))

            elif isinstance(logical, Function):
                return "{}({})".format(logical.name, ",".join(logical.variables))

            elif isinstance(logical, Negation):
                if isinstance(logical.terms[0], Negation):
                    # get rid of double negation
                    return ladr_logical(logical.terms[0].terms[0])
                elif isinstance(logical.terms[0], Predicate):
                    # put parentheses around single predicates to not mix them up with special-symbol predicates
                    return "-({})".format(ladr_logical(logical.terms[0]))
                else:
                    return "-{}".format(ladr_logical(logical.terms[0]))

            elif isinstance(logical, Conjunction):
                return "({})".format(" & ".join([ladr_logical(t) for t in logical.terms]))

            elif isinstance(logical, Disjunction):
                return "({})".format(" | ".join([ladr_logical(t) for t in logical.terms]))

            elif isinstance(logical, Conditional):
                return "({} -> {})".format(logical.terms[0],logical.terms[1])

            elif isinstance(logical, Biconditional):
                return "({} <-> {})".format(logical.terms[0],logical.terms[1])

            elif isinstance(logical, Universal):
                return "({} {})".format(("all {} " * len(logical.variables)).format(*logical.variables), ladr_logical(logical.terms[0]))

            elif isinstance(logical, Existential):
                return "({} {})".format(("exists {} " * len(logical.variables)).format(*logical.variables), ladr_logical(logical.terms[0]))

            else:
                raise ValueError("Not a valid type for LADR output")

        return "{}.".format(ladr_logical(self.sentence))

    def to_latex(self):
        """
        Produce a LADR representation of this axiom.

        :return str ladr, LADR formatted version of this axiom
        """

        def latex_logical(logical):

            if isinstance(logical, str):
                return logical

            elif isinstance(logical, Predicate):
                return "{}({})".format("\\textrm{" + logical.name.replace('_','\_') +"}", ",".join([latex_logical(t) for t in logical.variables]))

            elif isinstance(logical, Function):
                return "{}({})".format("\\textrm{" + logical.name.replace('_','\_') + "}", ",".join(logical.variables))

            elif isinstance(logical, Negation):
                if isinstance(logical.terms[0], Negation):
                    # get rid of double negation
                    return latex_logical(logical.terms[0].terms[0])
                elif isinstance(logical.terms[0], Predicate):
                    # put parentheses around single predicates to not mix them up with special-symbol predicates
                    return "\\neg \\left({}\\right)".format(latex_logical(logical.terms[0]))
                else:
                    return "\\neg {}".format(latex_logical(logical.terms[0]))

            elif isinstance(logical, Conjunction):
                return "\\left({}\\right)".format(" \\land ".join([latex_logical(t) for t in logical.terms]))

            elif isinstance(logical, Disjunction):
                return "\\left({}\\right)".format(" \\lor ".join([latex_logical(t) for t in logical.terms]))

            elif isinstance(logical, Conditional):
                return "\\left[ {} \\rightarrow {} \\right]".format(latex_logical(logical.terms[0]), latex_logical(logical.terms[1]))

            elif isinstance(logical, Biconditional):
                return "\\left[ {} \\leftrightarrow {} \\right]".format(latex_logical(logical.terms[0]), latex_logical(logical.terms[1]))

            elif isinstance(logical, Universal):
                return "{} \\left[ {} \\right]".format(("\\forall {}\\; " * len(logical.variables)).format(*logical.variables), latex_logical(logical.terms[0]))

            elif isinstance(logical, Existential):
                return "{} \\left[ {} \\right]".format(("\\exists {}\\; " * len(logical.variables)).format(*logical.variables), latex_logical(logical.terms[0]))

            else:
                raise ValueError("Not a valid type for LaTeX output")

        return "{}".format(latex_logical(self.sentence))


    def __repr__(self):

        return repr(self.sentence)
