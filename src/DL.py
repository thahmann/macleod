"""
@author Robert Powell
@version 0.0.4

The highlights.
"""

import os
os.sys.path.append('.')

import clif

"""
This section contains functions that try to simplify given FOL sentences
"""

def disjunctive_precondition(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[if cond1(...) | cond2(...) --> result(...)]

    into the form:

    forall(...)[if cond1 --> result(...)]
    forall(...)[if cond2 --> result(...)]
    """

    collection = []

    quantified = is_quantified(sentence)

    if not quantified:
        return False

    implication = is_implication(quantified)

    if not implication:
        return False

    precond = implication[0]
    result = implication[1]

    disjunction = is_disjunction(precond)

    if not disjunction:
        return False

    for thing in disjunction:

        statement = to_implication(thing, result)
        statement = to_quantified(sentence[1], statement)

        collection.append(statement)

    return collection

def conjuntive_implication(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[if binary(x, y) --> unary(x) & unary(y)

    into the form

    forall(x, y)[if binary(x, y) --> unary(x)]
    forall(x, y)]if binary(x, y) --> unary(y)]
    """

    collection = []

    quantified = is_quantified(sentence)

    if not quantified:
        return False

    implication = is_implication(quantified)

    if not implication:
        return False

    precond = implication[0]
    result = implication[1]

    conjunction = is_conjunction(result)

    if not conjunction:
        return False

    for thing in conjunction:

        statement = to_implication(precond, thing)
        statement = to_quantified(sentence[1], statement)

        collection.append(statement)

    return collection


def from_biconditional(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[expr_a(...) <--> expr_b(...)]

    into the form

    forall(...)[expr_a --> expr_b(...)]
    forall(...)[expr_b --> expr_a(...)]
    """

    collection = []

    quantified = is_quantified(sentence)

    if not quantified:
        return False

    implication = is_definition(quantified)

    if not implication:
        return False

    precond = implication[0]
    result = implication[1]

    collection.append(to_quantified(sentence[1], to_implication(precond, result)))
    collection.append(to_quantified(sentence[1], to_implication(result, precond)))

    return collection

def from_implication(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[E(...) --> B(...)]

    into the form

    ~(E(...)) --> B(...)
    """

    collection = []

    quantified = is_quantified(sentence)

    if not quantified:
        return False

    implication = is_implication(quantified)

    if not implication:
        return False

    precond = implication[0]
    conclusion = implication[1]

    negated_precond = to_negation(precond)

    return to_quantified(sentence[1], to_disjunction([negated_precond, conclusion]))

"""
End
"""

"""
This section contains functions to create new sentences
"""


def to_quantified(variables, expression):
    """
    Accept a set of variables and an expression they range over and return
    the result in the form of a universally quantified statement.
    """

    sentence = ['forall', variables, expression]
    return sentence

def to_implication(pre, post):
    """
    Accept two expressions and return them in the form of an implication.
    """

    implication = ['if', pre, post]

    return implication

def to_definition(pre, post):
    """
    Accept two expressions and return them in the form of a definition.
    """

    double_implication = ['iff', pre, post]

    return double_implication

def to_negation(expression):
    """
    Accept a list of elements and return them in a negated form
    """

    negation = ['not', expression]

    return negation

def to_conjunction(expressions):
    """
    Accept a number of expressions and return those in the form of
    a conjunction.
    """

    conjunction = ['and']

    for item in expressions:
        conjunction.append(item)

    return conjunction

def to_disjunction(expressions):
    """
    Accept a number of expressions and return those in the form of
    a disjunction.
    """

    disjunction = ['or']

    for item in expressions:
        disjunction.append(item)

    return disjunction

"""
END
"""

"""
This section provides functions for recognizing FOL patterns
"""

def is_conjunction(expression):
    """
    Determine if a passed expression is a conjunction
    """

    if expression[0] != 'and':
        return False

    return expression[1:]

def is_disjunction(expression):
    """
    Determine if a passed expression is a disjunction
    """

    if expression[0] != 'or':
        return False

    return expression[1:]

def is_implication(expression):
    """
    Determine if a passed expression is an implication
    """

    if expression[0] != 'if':
        return False

    return expression[1:]

def is_definition(expression):
    """
    Determine if a passed expression is a definition
    """

    if expression[0] != 'iff':
        return False

    return expression[1:]

def is_negated(symbol_expression):
    """
    Helper function to determine if a passed expression is negated or not.
    Negated expressions follow the form of:

        not [sub-expr]
    """

    if symbol_expression[0] != 'not':
        return False

    if len(symbol_expression) != 2:
        return False

    return symbol_expression[1]


def is_unary(symbol_expression):
    """
    Helper function to determine if a given predicate is unary or not. The
    sentence should only contain two elements: a nonlogical symbol and a
    variable.
    """

    if len(symbol_expression) != 2:
        return False

    for i in range(2):
        if not isinstance(symbol_expression[i], str):
            return False

    return True

def is_binary(expression):
    """
    Helper function to determine if a given predicate is a binary relation. The
    sentence should contain three elements: a nonlogical symbol followed by two
    variables.
    """

    if len(expression) != 3:
        return False

    for i in range(3):
        if not isinstance(expression[i], str):
            return False

    return True


def is_quantified(sentence):
    """
    Determines whether or not a sentence is universally quantified or not.

    TODO: Figure out how this should handle differently placed quantifiers.
    """

    if sentence[0] != 'forall':
        return False

    return sentence[2]

"""
END
"""

"""
This section contains functions that look for DL patterns in sentences
"""

def is_subclass(sentence):
    """
    Determines if the sentence contains a subclass relation. Subclass relations
    follow the form of:

        if Unary(x) --> Unary(y)

    where Unary(x) is the subclass of the Unary(y) relation.
    """

    implication = is_implication(sentence)

    if implication == False:
        return False

    if len(implication) != 2:
        return False

    if is_unary(implication[0]) == False:
        return False

    if is_unary(implication[1]) == False:
        return False

    return implication

def is_disjoint(sentence):
    """
    Determines if the sentence contains a disjoint relation. Disjoint relations
    follow the form of:

        if Unary(x) --> not Unary(y)

    where Unary(x) is disjoint with the Unary(y) relation.
    """

    implication = is_implication(sentence)

    if implication == False:
        return False

    # Check if 2nd term is negated
    negated = is_negated(implication[1])

    if negated == False:
        return False

    if is_unary(implication[0]) == False:
        return False

    if is_unary(negated) == False:
        return False

    return [implication[0], negated]

"""
END
"""

class CommonLogic(object):
    """
    A temporary class to help identify the pieces of a ClifModule that are
    important to this project. At the moment will serve as a nice holder for
    the sentences, symbols, and variables.
    """

    def __init__(self, sentences):

        self.sentences = sentences
        self.nonlogical_symbols = set()
        self.variables = set()

        self._init()

    def _init(self):
        """
        An abstracted startup function to extract the symbols, variables, etc
        from a collection of passed in sentences.

        :return None
        """

        for sentence in self.sentences[:]:

            symbols, _ = clif.get_nonlogical_symbols_and_variables(sentence)
            self.nonlogical_symbols |= symbols

def remove_biconditionals(sentences, simplified):
    """
    Recursive function to remove biconditional statements.
    """

    if len(sentences) == 0:
        return simplified

    else:

        sentence = sentences.pop()
        result = from_biconditional(sentence)

        if result:
            # Remember from_biconditional returns a list of lists
            sentences += result
        else:
            simplified.append(sentence)

    return remove_biconditionals(sentences, simplified)

if __name__ == '__main__':

    sentences = clif.get_sentences_from_file('qs/multidim_space_ped/ped.clif_backup')
    Common = CommonLogic(sentences)

    """
    Does the order of simplification have any side effects?

    Gonna just go with breaking down double implications first, then disjuntive preconditions,
    then finally the conjuntive results
    """



    derps = remove_biconditionals(sentences[:], [])

    for d in derps:
        print d
