"""
@author Robert Powell
@version 0.0.4

This is going to get worse before it gets better...
"""

import macleod.Clif as clif

def disjunctive_precondition(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[if cond1(...) | cond2(...) --> result(...)]

    into the form:

    forall(...)[if cond1 --> result(...)]
    forall(...)[if cond2 --> result(...)]
    """

    collection = []

    quantified = is_universal(sentence)

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
        statement = to_universal(sentence[1], statement)

        collection.append(statement)

    return collection

def conjuntive_conclusion(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[if binary(x, y) --> unary(x) & unary(y)

    into the form

    forall(x, y)[if binary(x, y) --> unary(x)]
    forall(x, y)]if binary(x, y) --> unary(y)]
    """

    collection = []

    quantified = is_universal(sentence)

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
        statement = to_universal(sentence[1], statement)

        collection.append(statement)

    return collection


def from_biconditional(sentence):
    """
    Attempt to simplify a sentence in the form:

    [expr_a(...) <--> expr_b(...)]

    into the form

    [expr_a --> expr_b(...) & expr_b --> expr_a(...)]
    """


    result = []

    biconditional = is_definition(sentence)


    if not biconditional:
        return False

    precond = biconditional[0]
    result = biconditional[1]

    left = to_implication(precond, result)
    right = to_implication(result, precond)

    conjunction = to_conjunction([left, right])

    return conjunction

def from_implication(sentence):
    """
    Attempt to simplify a sentence in the form:

    forall(...)[E(...) --> B(...)]

    into the form

    ~(E(...)) | B(...)
    """

    implication = is_implication(sentence)

    if not implication:
        return False

    precond = implication[0]
    conclusion = implication[1]

    negated_precond = to_negation(precond)

    return to_disjunction([negated_precond, conclusion])

def negate_negation(expression):
    """
    Simplify a double negated expression:

    not( not(something(...) ) ) into
    something(...)

    Assumes received expressions has already been stripped of leading 'not'
    """

    return expression[1]

def negate_conjunction(expression):
    """
    Simplify a negated conjunction:

    not( and( a_one, a_two, a__) ) into
    not(a_one) | not(a_one) | not(a__)

    Assumes received expressions has already been stripped of leading 'not'
    """

    negated_terms = [to_negation(term) for term in is_conjunction(expression)]
    return to_disjunction(negated_terms)

def negate_disjunction(expression):
    """
    Simplify a negated conjunction:

    not( or( a_one, a_two, a__) ) into
    not(a_one) & not(a_one) & not(a__)

    Assumes received expressions has already been stripped of leading 'not'
    """

    negated_terms = [to_negation(term) for term in is_disjunction(expression)]
    return to_conjunction(negated_terms)

def negate_existential(expression):
    """
    Simplify a negated existentially quantified scope:

    exists [y] [something(y)] into
    forall [y] not [something(y)]

    Assumes received expressions has already been stripped of leading 'not'
    """

    universal = to_universal(expression[1], to_negation(expression[2]))
    return universal

def from_negation(expression):
    """
    Attempt to push negation inwards within an expression

    # TODO What to do about negated quantifiers?

    I think in general anything that gets rid of a existential is good.
    However, my guess is that it's going to remove some of the OWL
    some-value-from interpretations. Then again, probably not because if it's
    equivalent then we should be able to spot that pattern in CNF and extract
    it.

    PUNT FOR NOW -- I'm forgetting something important about forall vs. exist
    """

    negated = is_negated(expression)

    # Just gonna be a little verbose for the time being

    conjunction = is_conjunction(negated)
    disjunction = is_disjunction(negated)
    existential = is_existential(negated)
    negation = is_negated(negated)

    if not negated:

        return False

    elif conjunction != False:

        return negate_conjunction(negated)

    elif disjunction != False:

        return negate_disjunction(negated)

    elif negation != False:

        return negate_negation(negated)

    elif existential != False:

        return negate_existential(negated)

    else:

        return False

def skolem_helper(x, variable, constant, expression):
    """
    Recursive helper
    """

    if isinstance(x, list):

        return skolemize_variable(variable, constant, x)

    elif x == variable:

        return constant

    else:

        return x

def skolemize_variable(variable, constant, expr):
    """
    Recursive helper function to dig through a sentence and replace all
    occurrences of a variable with a skolem constant.
    """

    return [skolem_helper(x, variable, constant, expr) for x in expr]


def from_existential(expression):
    """
    Attempt to skolemize an existentially quantified expression.
    """

    existential = is_existential(expression)

    if not existential:

        return False

    variables = expression[1]

    skolem = existential


    for index, var in enumerate(variables):

        # TODO Turn into function call with universal variables
        skolem = skolemize_variable(var, var.upper() + str(index), skolem)

    return skolem

def to_universal(variables, expression):
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
    Accept a list of elements and return them in a negated form. Does not
    automatically push the negation inwards.
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

def is_universal(sentence):
    """
    Determines whether or not a sentence is universally quantified or not.

    TODO: Figure out how this should handle differently placed quantifiers.
    """

    if sentence[0] != 'forall':
        return False

    return sentence[2]

def is_existential(sentence):
    """
    Determines whether or not a sentence is universally quantified or not.

    TODO: Figure out how this should handle differently placed quantifiers.
    """
    if sentence[0] != 'exists':
        return False

    return sentence[2]

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

def remove_biconditionals(sentence):
    """
    Recursive function to remove biconditional statements.
    """

    if not isinstance(sentence, list):

        return sentence

    definition = from_biconditional(sentence)

    if definition:

        return [remove_biconditionals(term) for term in definition]

    return [remove_biconditionals(term) for term in sentence]

def remove_implications(sentence):
    """
    Recursive function to remove sentences containing implications
    """

    if not isinstance(sentence, list):

        return sentence

    implication = from_implication(sentence)

    if implication:

        return [remove_implications(term) for term in implication]

    return [remove_implications(term) for term in sentence]

def distribute_negation(sentence):
    """
    Recurse over a sentence pushing all negation inwards

    # TODO Go back and understand how I came up with this!
    """

    if not isinstance(sentence, list):
        return sentence

    negated = is_negated(sentence)

    if negated:

        simplified = from_negation(sentence)

        if simplified:

            return [distribute_negation(term) for term in simplified]

    return [distribute_negation(term) for term in sentence]

def remove_existentials(sentence):
    """
    Recurse over a sentence skolemizing all existentially scoped variables
    """

    if not isinstance(sentence, list):

        return sentence

    existential = is_existential(sentence)

    if existential:

        skolemized = from_existential(sentence)

        if skolemized:

            return remove_existentials(skolemized)

    return [remove_existentials(term) for term in sentence]

def distribute_terms(disjunction_term, conjunction):
    """
    Perform simple distribution of terms.

    A OR (B AND C) ==> (A OR B) AND (A OR C)
    """

    expr = []

    conjunction_terms = is_conjunction(conjunction)

    if not conjunction_terms:

        return False

    for term in conjunction_terms:

        expr.append(to_disjunction([disjunction_term, term]))

    return to_conjunction(expr)

def to_cnf(sentence):
    """
    Recurse over a sentence and translate it into an equivalent CNF statement.

    Look for the pattern ['or', ... ,['and', ... ]]
    """

    if not isinstance(sentence, list):

        return sentence

    # If this is a disjunction it should only have conjunctive elements
    if is_disjunction(sentence):

        disjunction = is_disjunction(sentence)

        for sub_element in disjunction:

            if is_conjunction(sub_element):

                # Find a different element in sentence
                disjunctive_term = disjunction[0]

                if disjunctive_term == sub_element:

                    disjunctive_term = disjunction[1]

                conjunction = distribute_terms(disjunctive_term, sub_element)

                return [to_cnf(elm) for elm in conjunction]

    return [to_cnf(sub) for sub in sentence]


if __name__ == '__main__':

    import pprint

    sentences = clif.get_sentences_from_file('qs/multidim_space_ped/ped.clif_backup')
    pprint.pprint(sentences)

    print('Done')

    Common = CommonLogic(sentences)


    for s in sentences:
        a = remove_biconditionals(s)
        b = remove_implications(a)
        c = distribute_negation(b)
        #d = remove_existentials(c)

        q = to_cnf(c)
        pprint.pprint(q)






