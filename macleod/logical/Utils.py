"""
Insert boss header here
@RPSkillet
"""

import logging

import macleod.logical.Negation as Negation
import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier

LOGGER = logging.getLogger(__name__)

def dfs_functions(term, accumulator, parent):
    """
    Recursive utility function to traverse over a Logical in search of
    Predicates that have nested functions. Upon finding such a predicate call
    substitute on the term
    """

    if isinstance(term, Symbol.Predicate):

        if term.has_functions():

            if isinstance(parent, Negation.Negation):
                clause, axiom = term.substitute_function(negated=True)

                # Hack to workaround having to patch grandparent term link
                clause = ~clause

            else:
                clause, axiom = term.substitute_function()

            accumulator.append(axiom)

            return dfs_functions(clause, accumulator, term)

        else:

            return term

    if isinstance(term, Quantifier.Quantifier):

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

def dfs_standardize(term, gen, translations=[]):
    """
    Recurse over a logical applying variable substitution to ensure only unique
    variables exists.
    """

    if isinstance(term, Symbol.Predicate):

        left = len(term.variables)

        for idx, var in enumerate(term.variables):

            for trans in reversed(translations):

                if var in trans:

                    term.variables[idx] = trans[var]
                    left -= 1
                    break

        if left != 0:
            LOGGER.warning("Found a constant!")
            #raise ValueError("Found a free variable!")

        return term

    elif isinstance(term, Quantifier.Quantifier):

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

    if isinstance(term, Symbol.Predicate):
        return term
    elif isinstance(term, Quantifier.Quantifier):
        return type(term)(term.variables, [dfs_negate(x) for x in term.get_term()])
    elif isinstance(term, Negation.Negation):
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

        if not isinstance(current, Symbol.Predicate):

            # If care about L->R order do reversed(current.get_term())
            left.extend([(x, current) for x in current.get_term()])

    return reversed(accumulator)
