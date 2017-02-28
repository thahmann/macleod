"""
@author Robert Powell
@version 0.0.4

This is going to get worse before it gets better...
"""

import macleod.Clif as clif
import pprint


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

    if not isinstance(symbol_expression, list):
        return False

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
    if not isinstance(expression, list):
        return False

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
    param: list sentence, FOL sentence
    return: list/boolean, sentence or false
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

#def strip_quantifier(sentence):
#    '''
#    Attempt to remove all quantifiers found in a FOL sentence.
#
#    :param list FOL sentence
#    :return list, FOL with no quantifications
#    '''
#
#    stripped = strip_quantifiers(sentence)
#
#    return [strip_quantifiers(x) for x in stripped]

def strip_quantifier(sentence):
    '''
    Attempt remove to quantifiers at the beginning of a sentence until only predicates
    and logical symbols remain. Assumes quantifiers are chained at beginning of
    sentence.

    :param list sentence, the quantified sentence
    :return list sentence, sentence with quantifiers stripped
    '''

    if not isinstance(sentence, list):
        return sentence

    existential = is_existential(sentence)
    universal = is_universal(sentence)

    if existential != False:
        return strip_quantifier(existential)

    if universal != False:
        return strip_quantifier(universal)

    return [strip_quantifier(x) for x in sentence]

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


def distribute_negation(sentence, modified):
    '''
    Recurse over a sentence pushing all negation inwards

    :param list sentence, FOL sentence
    :param list modified, flag indcating changes occured
    :return list sentence
    '''

    if not isinstance(sentence, list):
        return sentence

    negated = is_negated(sentence)

    if negated:

        simplified = from_negation(sentence)

        if simplified:

            modified.append(True)
            return [distribute_negation(term, modified) for term in simplified]

    return [distribute_negation(term, modified) for term in sentence]

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

def get_quantifier_order(sentence):
    '''
    Wrapper function around get_quantifier_order_recursive

    :param list sentence, FOL sentence
    :return list sentence, same sentence with quantifiers pulled to front
    '''

    acc = []
    get_quantifier_order_recursive(sentence[:], acc)

    quantifier_order = [acc.pop(0)]

    while len(acc) != 0:

        quantifier, variables = acc.pop(0)
        if  quantifier == quantifier_order[-1][0]:
            quantifier_order[-1][1] += variables
        else:
            quantifier_order.append([quantifier, variables])

    return quantifier_order

def get_quantifier_order_recursive(sentence, acc):
    '''
    Recursively pull the quantifier order of a FOL sentence without
    changing the meaning of the sentence. Do this with a breadth first traversal
    of the sentence aggregating the same type of quantifiers.

    :param list sentence, FOL sentence
    :param list accumulator
    :return None
    '''

    if not isinstance(sentence, list):

        return acc

    if is_existential(sentence):

        # Don't want to add variables to existing list
        quantifier = 'exists'
        variables = sentence[1][:]

        for term in sentence:

            if is_existential(term):
                variables += term[1][:]

        acc.append([quantifier, variables])

    elif is_universal(sentence):

        # Don't want to add variables to existing list
        quantifier = 'forall'
        variables = sentence[1][:]

        for term in sentence:

            if is_universal(term):
                variables += term[1][:]

        acc.append([quantifier, variables])


    [get_quantifier_order_recursive(x, acc) for x in sentence]

def remove_nesting_helper(sentence, modified):
    '''
    Helper function to remove nesting found within the CNF sentence.

    :param list sentence, input FOL sentence
    :return list sentence, simplified FOL sentence
    '''

    return [remove_nesting(x, modified) for x in sentence]

def remove_nesting(sentence, modified):
    '''
    Recurse over a sentence and remove redundant nesting.

    :param list sentence, input FOL sentence
    :return list sentence, simplified FOL sentence
    '''

    if not isinstance(sentence, list):

        return sentence

    new_sentence = []

    conjunction = is_conjunction(sentence)
    disjunction = is_disjunction(sentence)

    if conjunction:

        while len(conjunction) != 0:

            term = conjunction.pop()
            nested_conjunction = is_conjunction(term)

            if nested_conjunction:
                modified.append(True)
                new_sentence += nested_conjunction
            else:
                new_sentence.append(term)

        return remove_nesting_helper(to_conjunction(new_sentence), modified)

    elif disjunction:

        while len(disjunction) != 0:

            term = disjunction.pop()
            nested_disjunction = is_disjunction(term)

            if nested_disjunction:
                modified.append(True)
                new_sentence += nested_disjunction
            else:
                new_sentence.append(term)

        return remove_nesting_helper(to_disjunction(new_sentence), modified)

    else:

        return remove_nesting_helper(sentence, modified)

def rename_all_variables(sentence, variables):
    '''
    Helper function

    :param list sentence
    :param dict variables
    '''

    if not isinstance(sentence, list):

        if sentence in variables:

            sentence = variables[sentence]

        return sentence

    return [rename_all_variables(x, variables) for x in sentence]

def rename_variables(sentence, depth, variables):
    '''
    Function to recursively rename variables according to scoped quantifiers

    :param list sentence
    :param int depth
    :param dict variables
    '''

    if not isinstance(sentence, list):

        if sentence in variables:
            sentence = sentence + str(depth)

        return sentence

    universal = is_universal(sentence)
    existential = is_existential(sentence)

    if universal or existential:

        depth = depth + 1

        variables = {}
        for new_variable in sentence[1]:

            variables[new_variable] = new_variable + str(depth)

            sentence = rename_all_variables(sentence, variables)

    return [rename_variables(x, depth, variables) for x in sentence]

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

def to_cnf(sentence, modified):
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

                # Make sure to not drop remainder of original disjunction
                remainder = [x for x in disjunction if x != disjunctive_term and x != sub_element]

                if len(remainder) != 0:
                    remainder.append(conjunction)
                    new_term = to_disjunction(remainder)
                else:
                    new_term = conjunction

                modified.append(True)
                return [to_cnf(elm, modified) for elm in new_term]

    return [to_cnf(sub, modified) for sub in sentence]


def get_universally_quantified(sentence, variables):
    '''
    Given a FOL sentence return all universally quantified variables

    :param list sentence, FOL sentence
    :return list variables, universally quantified variables
    '''

    if not isinstance(sentence, list):
        return None

    universal = is_universal(sentence)

    if universal != False:
        variables += sentence[1]

    for element in sentence:

        get_universally_quantified(element, variables)

def get_existentially_quantified(sentence, variables):
    '''
    Given a FOL sentence return all existentially quantified variables

    :param list sentence, FOL sentence
    :return list variables, universally quantified variables
    '''

    if not isinstance(sentence, list):
        return None

    existential = is_existential(sentence)

    if existential != False:
        variables += sentence[1]

    for element in sentence:

        get_existentially_quantified(element, variables)

def translate_sentence(sentence):
    '''
    Given a sentence in FOL break it down into a quasi conjuntive normal form.
    Specifically,
        1. Simplify biconditionals
        2. Simplify implications
        3. Distribute negation
        4. Put into conjunctive normal form**

    **Doesn't skolemize existential quantifiers.

    :param list sentence, FOL sentence
    :return list CNF, equivalent FOL sentence in near CNF form
    '''

    renamed = rename_variables(sentence, 0, [])
    quantifiers = get_quantifier_order(renamed)
    simplified = strip_quantifier(renamed)

    implications = remove_biconditionals(simplified)
    simplified = remove_implications(implications)


    distributed = distribute_negation(simplified, [])
    distributing = True
    while distributing:

        distributing = False
        modified_distribution = [True]
        modified_nesting = [True]

        while len(modified_distribution) != 0:
            modified_distribution[:] = []
            distributed = distribute_negation(distributed, modified_distribution)

            if len(modified_distribution) != 0:
                distributing = True


        while len(modified_nesting) != 0:
            modified_nesting[:] = []
            distributed = remove_nesting(distributed, modified_nesting)

            if len(modified_nesting) != 0:
                distributing = True

    cnf = to_cnf(distributed, [])
    normalizing = True

    while normalizing:

        normalizing = False
        modified_normalization = [True]
        modified_nesting = [True]

        while len(modified_normalization) != 0:
            modified_normalization[:] = []
            cnf = to_cnf(cnf, modified_normalization)

            if len(modified_normalization) != 0:
                normalizing = True

        while len(modified_nesting) != 0:
            modified_nesting[:] = []
            cnf = remove_nesting(cnf, modified_nesting)

            if len(modified_nesting) != 0:
                normalizing = True

    return [quantifiers, cnf]

if __name__ == '__main__':


    SENTENCES = clif.get_sentences_from_file('../../qs/multidim_space_ped/ped.clif_backup')

    for s in SENTENCES:

        translated = translate_sentence(s)

        translation, quantifiers = translated.pop(), translated.pop()
        unary_predicates = []
        binary_predicates = []

        print('____________________')
        pprint.pprint(s)
        print('')
        print (quantifiers)
        pprint.pprint(translation, width=60)
        print()
        print('____________________')
