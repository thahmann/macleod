"""
Insert boss header here
@RPSkillet
"""

import copy
import logging

from macleod.logical.negation import Negation
from macleod.logical.symbol import (Function, Predicate)
from macleod.logical.quantifier import (Universal, Existential, Quantifier)

LOGGER = logging.getLogger(__name__)

def dfs_functions(term, accumulator, parent):
    """
    Recursive utility function to traverse over a Logical in search of
    Predicates that have nested functions. Upon finding such a predicate call
    substitute on the term
    """

    if isinstance(term, Predicate):

        if term.has_functions():

            if isinstance(parent, Negation):
                clause, axiom = term.substitute_function(negated=True)

                # Hack to workaround having to patch grandparent term link
                clause = ~clause

            else:
                clause, axiom = term.substitute_function()

            accumulator += axiom

            return dfs_functions(clause, accumulator, term)

        else:

            return term

    if isinstance(term, Quantifier):

        return type(term)(term.variables, [dfs_functions(x, accumulator, term) for x in term.get_term()])

    else:

        return type(term)([dfs_functions(x, accumulator, term) for x in term.get_term()])

def generator():
    """
    Return a sequence of ASCII characters starting a z in reverse order. Raise
    an error if too many characters are requested.
    """

    start = 122

    def next_term():

        nonlocal start

        character = chr(start)
        start -= 1

        if start == 96:

            raise ValueError("Look man, 26 variables is just too many. I'm not going to even try")

        return character

    return next_term

def quote_constants(term, constants):

    def substitute_constants_in_term(term, constants):

        if isinstance(term, str):
            # do the real substitution here
            for c in constants:
                #print("REPLACING Constant " + c)
                return term.replace(c, "'" + c + "'")

        if isinstance(term, Predicate) or isinstance(term, Function):
            return type(term)(term.name, [substitute_constants_in_term(x, constants) for x in term.variables])
        if isinstance(term, Quantifier):
            return type(term)([substitute_constants_in_term(x, constants) for x in term.variables], [substitute_constants_in_term(x, constants) for x in term.terms])
        else:
            return type(term)([substitute_constants_in_term(x, constants) for x in term.get_term()])

    constants_copy = copy.deepcopy(constants)
    constants_copy.sort(key=len, reverse=True)

    for c in constants_copy:
        if c.isalnum():
            constants_copy.remove(c)

    #print("Constants: " + str(constants_copy))

    if len(constants_copy) == 0:
        return term
    else:
        term = substitute_constants_in_term(term, constants_copy)
        print ("New string " + repr(term))
        return term


def dfs_standardize(term, gen, translations=[]):
    """
    Recurse over a logical applying variable substitution to ensure only unique
    variables exists.
    """

    if isinstance(term, Predicate):

        left = len(term.variables)

        for idx, var in enumerate(term.variables):

            for trans in reversed(translations):

                if var in trans:

                    term.variables[idx] = trans[var]
                    left -= 1
                    break

        if left != 0:
            LOGGER.info("Found a constant!")

            # TODO: can we substitute constants with special symbols here?


            #raise ValueError("Found a free variable!")

        return term

    elif isinstance(term, Quantifier):

        lookup_table = {}

        for idx, var in enumerate(term.variables):

            lookup_table[var] = gen()
            term.variables[idx] = lookup_table[var]

        translations.append(lookup_table)
        return type(term)(term.variables, [dfs_standardize(x, gen, translations) for x in term.get_term()])
    else:
        return type(term)([dfs_standardize(x, gen, translations) for x in term.get_term()])

def dfs_negate(term):
    """
    Recurse over a logical repeatedly pushing negation deeper into the object
    tree.
    """

    if isinstance(term, Predicate):
        return term
    elif isinstance(term, Quantifier):
        return type(term)(term.variables, [dfs_negate(x) for x in term.get_term()])
    elif isinstance(term, Negation):
        return term.push_complete()
    else:
        return type(term)([dfs_negate(x) for x in term.get_term()])

def reverse_bfs(root):
    """
    Conduct a regular BFS over the tree packing each layer into a list
    of [(term, parent), ...] and return it
    """

    accumulator = []
    left = [(root, None)]

    while left != []:

        current, parent = left.pop(0)
        accumulator.append((current, parent))

        if not isinstance(current, Predicate):

            # If care about L->R order do reversed(current.get_term())
            left.extend([(x, current) for x in current.get_term()])

    return reversed(accumulator)
