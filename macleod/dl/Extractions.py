"""
@author Robert Powell
@version 0.0.4

Module that contains each of the translated DL axioms
"""

import pprint as pp
import argparse
import tempfile
import copy

import macleod.Clif as clif
import macleod.dl.Translation as Translation
import macleod.dl.DL as DL
import macleod.dl.Utilities as Util

TMPDIR = "/tmp"
EQ = "="

def filter_on_quantifiers(sentence, quantifiers, extractions):
    '''
    Filter the number of possible extractions from an axiom based on number of
    quantifiers.
    '''

    # Copy the array of extractions to be whittled down
    extractions = EXTRACTIONS.copy()

    num_of_quantifiers = count_quantifiers(quantifiers)

    # --- Begin Single Var Only ---
    # Extractions =
    # Universal Domain Restriction
    # Disjoint Classes
    # Subclass
    # Equivalent Classes
    # Disjoint Union
    # Reflexive Property
    # Irreflexive Property

    # --- Begin Double Var Only ---
    # Universal Property Restriction
    # Disjoint Properties
    # Asymmetric Property
    # Sub-Property
    # Equivalent Properties
    # Inverted Sub-Property
    # Inverse Property
    # Symmetric Property
    # Property Domain Restriction
    # Property Range Restriction

    # --- Begin Triple Var Only ---
    # Functional Property
    # Inverse Functional Property

    if num_of_quantifiers == 1:
        return filter_on_variables(sentence, quantifiers, extractions)
    else:
        return []

# SECOND
def filter_on_variables(sentence, quantifiers, extractions):
    '''
    Filter the number of possible extractions from an axiom based on number of
    variables.
    '''

    num_of_variables = count_variables(sentence)

    if num_of_variables == 1:

        local_set = {extract_domain_restriction, extract_disjoint_relation,
                     extract_subclass_relation,
                     extract_reflexive_relation,
                     extract_irreflexive_relation}

        extractions = extractions & local_set
        return filter_on_predicates(sentence, quantifiers, extractions)

    elif num_of_variables == 2:

        local_set = {extract_asymmetric_relation, extract_subproperty_relation,
                     extract_inverse_relation,
                     extract_inverted_subproperty_relation,
                     extract_symmetric_relation,
                     extract_property_domain_restriction,
                     extract_property_range_restriction}

        extractions = extractions & local_set
        return filter_on_predicates(sentence, quantifiers, extractions)

    elif num_of_variables == 3:

        local_set = {extract_functional_relation,
                     extract_inverse_functional_relation}

        extractions = extractions & local_set
        return extractions
    else:
        return []

# THIRD
def filter_on_predicates(sentence, quantifiers, extractions):
    '''
    Filter the number of possible extractions from an axiom based on types of
    predicates.
    '''

    if DL.is_all_unary(sentence):

        local_set = {extract_domain_restriction, extract_disjoint_relation,
                     extract_subclass_relation
                     }

        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

    elif DL.is_all_binary(sentence):

        local_set = {extract_disjoint_properties, extract_asymmetric_relation,
                     extract_subproperty_relation,
                     extract_inverted_subproperty_relation,
                     extract_inverse_relation, extract_symmetric_relation,
                     extract_reflexive_relation}

        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

    else:

        local_set = {extract_property_domain_restriction,
                     extract_property_range_restriction}
        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

# FOURTH
def filter_on_sign(sentence, _quantifiers, extractions):
    '''
    Filter the number of possible extractions from an axiom based on types of
    predicates signs
    '''

    if DL.is_all_positive(sentence):

        local_set = {extract_domain_restriction, extract_reflexive_relation}

        extractions = extractions & local_set
        return extractions

    elif DL.is_all_negative(sentence):

        local_set = {extract_disjoint_relation, extract_disjoint_properties,
                     extract_irreflexive_relation, extract_asymmetric_relation}

        extractions = extractions & local_set
        return extractions

    else:

        local_set = {extract_subclass_relation,
                     extract_subproperty_relation,
                     extract_inverted_subproperty_relation,
                     extract_inverse_relation,
                     extract_symmetric_relation,
                     extract_property_domain_restriction,
                     extract_property_range_restriction}

        extractions = extractions & local_set
        return extractions


def narrow_translations(sentence, quantifiers):
    '''
    Filtering function to narrow down possible translations to try on a given
    sentence.

    :param list sentence, FOL sentence in CNF* form.
    :return list translators, list of applicable translation functions
    '''

    return filter_on_quantifiers(sentence, quantifiers, {})

def count_construct(axiom, comparison):
    '''
    Simplified function to make counting easier
    '''

    count = 0

    for term in axiom:

        if comparison(term):

            count += 1

    return count

def count_negated_terms(axiom):
    '''
    Count the number of negated predicates in an axiom
    '''

    return count_construct(axiom, Translation.is_negated)

def count_unary_terms(axiom):
    '''
    Count the number of unary predicates in an axiom
    '''

    return count_construct(axiom, Translation.is_unary)

def count_binary_terms(axiom):
    '''
    Count the number of binary predicates in an axiom
    '''

    return count_construct(axiom, Translation.is_binary)

def count_clauses(axiom):
    '''
    Counts the number of clauses in a axiom
    '''

    return len(axiom) - 1

def count_quantifiers(quantifiers):
    '''
    Wrapper function to count the number of quantifiers for a given axiom
    '''

    count = 0

    for q in quantifiers:
        count += count_quantifiers_helper(q)

    return count

def count_quantifiers_helper(quantifiers):
    '''
    Counts the number of quantifiers in a given axiom. Assumes that it has been
    passed a top level quantifier, not a list of top level quantifiers

    '''

    if quantifiers[2] == []:

        return 1

    else:

        return 1 + sum([count_quantifiers_helper(q) for q in quantifiers[2]])


def count_variables(axiom):
    '''
    Returns the number of variables actually used in the clause, as opposed to
    over the entire conjunction it may be part of.
    '''

    variables = set()

    for clause in axiom:

        if Translation.is_negated(clause):

            clause = Translation.is_negated(clause)

        if Translation.is_unary(clause):

            variables.add(clause[1])

        elif Translation.is_binary(clause):

            variables.add(clause[1])
            variables.add(clause[2])

    return len(variables)

def count_universal(quantifiers):
    '''
    Returns the number of universally quantified variables

    '''

    quantified_variables = []
    for quantifier in quantifiers:
        Translation.get_universally_quantified(quantifier, quantified_variables)

    return len(quantified_variables)

def count_existential(quantifiers):
    '''
    Returns the number of universally quantified variables

    '''

    quantified_variables = []
    for quantifier in quantifiers:
        Translation.get_existentially_quantified(quantifier, quantified_variables)

def same_variables(pred_one, pred_two):
    '''
    Returns true if both predicates are over the same variable
    '''

    if Translation.is_negated(pred_one):
        pred_one = Translation.negate_negation(pred_one)

    if Translation.is_negated(pred_two):
        pred_two = Translation.negate_negation(pred_two)

    if Translation.is_unary(pred_one) and Translation.is_unary(pred_two):

        if pred_one[1] == pred_two[1]:
            return True

    if Translation.is_binary(pred_one) and Translation.is_binary(pred_two):

        if pred_one[1] == pred_two[1] and pred_one[2] == pred_two[2]:
            return True

    return False

def extract_subclass_relation(axiom, _quantifiers):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    # More than one means intersection of terms
    subset = []
    DL.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    # More than one means union of terms
    unary = []
    DL.find_unary_predicates(axiom, unary)
    superset = [x for x in unary if x not in subset]

    subset = list(map(get_predicate_name, subset))
    superset = list(map(get_predicate_name, superset))

    return ('subclass', subset, superset)

def extract_functional_relation(axiom, _quantifier):
    '''
    Assumes two predicates, one of which is the Equality predicate. The
    non-equality predicate is negated and appears twice. Both instances will
    share the same variable for domain, but different variable for range. One
    predicate will share domain with equality, the other will share range with
    equality.
    '''

    if count_clauses(axiom) != 3:
        return

    clauses = []
    DL.find_binary_predicates(axiom, clauses)

    if len(clauses) != 3:
        return

    equality = [x for x in clauses if get_predicate_name(x) == EQ]

    if len(equality) != 1:
        return

    negated = []
    DL.find_negated_predicates(axiom, negated)
    negated = [Translation.negate_negation(x) for x in negated]


    if len(negated) != 2:
        return

    if any([x[0] == EQ for x in negated]):
        return

    if get_predicate_name(negated[0]) != get_predicate_name(negated[1]):
        return

    if same_variables(negated[0], negated[1]):
        return

    if negated[0][1] != negated[1][1]:
        return

    if (negated[0][2] != equality[0][2]) and (negated[1][2] != equality[0][2]):
        return

    if (negated[0][2] != equality[0][1]) and (negated[1][2] != equality[0][1]):
        return

    return ('functional_property', get_predicate_name(negated[0]))

def extract_inverse_functional_relation(axiom, _quantifier):
    '''
    Assumes two predicates, one of which is the Equality predicate. The
    non-equality predicate is negated and appears twice. Both instances will
    share the same variable for domain, but different variable for range. One
    predicate will share domain with equality, the other will share range with
    equality.
    '''

    if count_clauses(axiom) != 3:
        return

    clauses = []
    DL.find_binary_predicates(axiom, clauses)

    if len(clauses) != 3:
        return

    equality = [x for x in clauses if get_predicate_name(x) == EQ]

    if len(equality) != 1:
        return

    negated = []
    DL.find_negated_predicates(axiom, negated)
    negated = [Translation.negate_negation(x) for x in negated]


    if len(negated) != 2:
        return

    if any([x[0] == EQ for x in negated]):
        return

    if get_predicate_name(negated[0]) != get_predicate_name(negated[1]):
        return

    if same_variables(negated[0], negated[1]):
        return

    if negated[0][2] != negated[1][2]:
        return

    if (negated[0][1] != equality[0][2]) and (negated[1][1] != equality[0][2]):
        return

    if (negated[0][1] != equality[0][1]) and (negated[1][1] != equality[0][1]):
        return

    return ('inverse_functional_property', get_predicate_name(negated[0]))

def extract_property_domain_restriction(axiom, _quantifier):
    '''
    Assumes a single negated binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''

    prop = []
    DL.find_binary_predicates(axiom, prop)

    classes = []
    DL.find_unary_predicates(axiom, classes)

    if any([Translation.is_negated(x) for x in classes]):
        return

    if len(prop) != 1:
        return

    if any([not same_variables(classes[0], x) for x in classes]):
        return

    if classes[0][1] != prop[0][1]:
        return

    prop = [get_predicate_name(x) for x in prop]
    classes = [get_predicate_name(y) for y in classes]

    return ('property_domain_restriction', prop, classes)

def extract_property_range_restriction(axiom, _quantifier):
    '''
    Assumes a single negated binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''

    prop = []
    DL.find_binary_predicates(axiom, prop)

    classes = []
    DL.find_unary_predicates(axiom, classes)

    if any([Translation.is_negated(x) for x in classes]):
        return

    if len(prop) != 1:
        return

    if any([not same_variables(classes[0], x) for x in classes]):
        return

    if classes[0][1] != prop[0][2]:
        return

    prop = [get_predicate_name(x) for x in prop]
    classes = [get_predicate_name(y) for y in classes]

    return ('property_range_restriction', prop, classes)

def extract_symmetric_relation(axiom, _quantifiers):
    '''
    Assume single binary predicate appearing twice, one negated and one not negated. Variables
    should be in reversed positions in each predicate.
    '''

    prop = []
    DL.find_binary_predicates(axiom, prop)

    if len(prop) != 2:
        return

    if prop[0][0] != prop[1][0]:
        return

    if not any([Translation.is_negated(x) for x in prop]):
        return

    if same_variables(prop[0], prop[1]):
        return

    return ('symmetric_relation', get_predicate_name(prop[0]))

def extract_asymmetric_relation(axiom, _quantifier):
    '''
    Assume single binary predicate appearing twice, both negated. Variables
    should be in reversed positions in each predicate.
    '''

    prop = []
    DL.find_binary_predicates(axiom, prop)

    if len(prop) != 2:
        return

    if prop[0][0] != prop[1][0]:
        return

    if same_variables(prop[0], prop[1]):
        return

    return ('asymmetric_relation', get_predicate_name(prop[0]))

def extract_disjoint_relation(axiom, _quantifiers):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least two negative terms. Only a single universally quantified variable.
    '''

    # More than one means intersection of terms
    classes = []
    DL.find_negated_predicates(axiom, classes)
    classes = [Translation.negate_negation(x) for x in classes]

    classes = list(map(get_predicate_name, classes))

    return ('disjoint_classes', classes[0], classes[1])

def extract_disjoint_properties(axiom, _quantifiers):
    '''
    Assumes that all predicates are binary, it's a disjunction, and there exists
    at least two negative terms. Only a single universally quantified variable.
    '''

    # More than one means intersection of terms
    props = []
    DL.find_negated_predicates(axiom, props)
    props = [Translation.negate_negation(x) for x in props]

    if not all([same_variables(props[0], x) for x in props]):
        return

    props = list(map(get_predicate_name, props))

    return ('disjoint_properties', props[0], props[1])

def extract_domain_restriction(axiom, _quantifiers):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    restriction = list(map(get_predicate_name, axiom[1:]))

    return ('universe_restriction', restriction)

def extract_subproperty_relation(axiom, _quantifiers):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    # More than one means intersection of terms
    subset = []
    DL.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    # More than one means union of terms
    binary = []
    DL.find_binary_predicates(axiom, binary)
    superset = [x for x in binary if x not in subset]

    for predicate in subset[:] + superset[:]:

        if not same_variables(subset[0], predicate):
            return

    subset = list(map(get_predicate_name, subset))
    superset = list(map(get_predicate_name, superset))



    return ('subproperty', subset, superset)

def extract_inverted_subproperty_relation(axiom, _quantifiers):
    '''
    Assumes that all predicates are binary, it's a disjunction, and there exists
    one negative term and one positive term. Only a single universally
    quantified variable. This is a partial to the inverse object property, two
    of these over the same predicates but reversed will be detected as the
    former.
    '''

    # More than one means intersection of terms
    subset = []
    DL.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    if len(subset) != 1:
        return

    # More than one means union of terms
    binary = []
    DL.find_binary_predicates(axiom, binary)
    superset = [x for x in binary if x not in subset]

    if len(superset) != 1:
        return

    for predicate in subset[:] + superset[:]:

        if same_variables(subset[0], predicate):
            return

    subset = list(map(get_predicate_name, subset))
    superset = list(map(get_predicate_name, superset))

    return ('inverted_subproperty', subset, superset)

# TODO Find an object inverse relation with two inverted subproperties
def extract_inverse_relation(a, q):
    pass

def extract_reflexive_relation(axiom, _quantifiers):
    '''
    Assumes that the predicate is binary and only a single universally
    quantified variable is used.
    '''

    reflexive_property = get_predicate_name(axiom[0])

    return ('reflexive', reflexive_property)

def extract_irreflexive_relation(axiom, _quantifiers):
    '''
    Assumes that the predicate is negated, binary, and only a single universally
    quantified variable is used.
    '''

    reflexive_property = list(map(get_predicate_name, axiom[1:]))

    return ('reflexive', reflexive_property)

def get_predicate_name(predicate):
    '''
    Returns a predicates symbol, minus the variables
    '''

    return predicate[0]

def extract_conjuncts(sentence):
    '''
    Accepts a conjunction and returns a list of individual conjuncts to be
    examined later
    '''

    axioms = []

    if Translation.is_conjunction(sentence):
        axioms += Translation.is_conjunction(sentence)
    elif Translation.is_disjunction(sentence):
        axioms = [sentence]
    else:
        print("Don't know when this could ever happen")
        print("We're going down captain!")

    return axioms

def generate_quantifier(sentence, quantifiers):
    '''
    Take a sentence and set of quantifiers and trim the quantifiers so only
    variables in the sentence exist in the quantifier. Return the new
    quantifier and sentence together in a list.

    return list axiom, [[quantifiers], [sentence]]
    '''

    new_quantifiers = quantifiers[:]

    predicates = []
    DL.find_binary_predicates(sentence, predicates)
    DL.find_unary_predicates(sentence, predicates)
    predicates = list(set([get_predicate_name(p) for p in predicates]))

    #print("[+] Found Predicates:", predicates)

    quantified_variables = []
    for quantifier in new_quantifiers:
        Translation.get_universally_quantified(quantifier, quantified_variables)
        Translation.get_existentially_quantified(quantifier, quantified_variables)

    quantified_variables = list(set(quantified_variables))

    #print("[+] Found Quantified Variables:", quantified_variables)

    flattened_axiom = list(set(list(Util.flatten(sentence))))

    variables = list(filter(Translation.is_nonlogical, flattened_axiom))
    variables = [v for v in variables if v not in predicates]

    #print("[+] Found Variables:", variables)

    variables_to_trim = [v for v in quantified_variables if v not in variables]

    #print("[+] Removing Variables:", variables_to_trim)

    #print("[+] Starting Quantifier:", new_quantifiers)

    new_quantifiers = trim_quantifier(new_quantifiers, variables_to_trim)

    #print("[+] Generated Quantifier:", new_quantifiers)

    return [copy.deepcopy(new_quantifiers), copy.deepcopy(sentence)]

def trim_quantifier(quantifiers, variables):
    '''
    Utility function combing the trim_quantifier and restructure_quantifier
    functionality
    '''

    for quantifier in quantifiers:
        trim_variables(quantifier, variables)

    while True:

        add_list = []
        remove_list = []
        for quantifier in quantifiers:
            result = restructure_quantifier(quantifier)

            if result:
                add_list = result
                remove_list.append(quantifier)

        if len(add_list) == 0:
            break
        else:
            quantifiers += add_list
            _ = [quantifiers.remove(x) for x in remove_list]

    return quantifiers

def trim_variables(quantifiers, variables):
    '''
    Search through a nested quantifier structure and remove the given
    variables. Trim the nested structure as needed if all the variables are
    removed from a given quantifier then cry yourself to sleep because that's
    another boundary/theoretical problem to worry about.

    :param list quantifiers, nested quantifiers
    :param list variables, list of variables to be removed
    :return None
    '''

    if not isinstance(quantifiers, list):
        return

    # Remove variables if present in both lists
    quantifiers[1] = [v for v in quantifiers[1] if v not in variables]

    # In the case of a missing parent, just promote any present children
    if len(quantifiers[1]) == 0:
        quantifiers[0] = []

    if len(quantifiers) >= 2:
        _ = [trim_variables(q, variables) for q in quantifiers[2]]

def restructure_quantifier(quantifier):
    '''
    Utility function to fix the overall structure of quantifiers after trimming
    occurs. If any quantifier quantifies no variables, replace it with any
    nested quantifiers if they exist. Otherwise, empty the whole list. In the
    case where a previously top-level quantifier is removed the function will
    return a new list of quantifiers to be located at the top level.

    :param list quantifier, potentially de-structured quantifier
    :return list/None, interrupt result
    '''

    #print (quantifier)

    if not isinstance(quantifier, list):
        return

    # Special case to handle when the top-level quantifier gets removed
    # Return the new quantifier
    if quantifier[0] == []:

        new_quantifier = copy.deepcopy(quantifier[2])
        return new_quantifier

    # If quantifier has no empty children continue down the tree
    if not any([True for x in quantifier[2] if len(x[1]) == 0]):

        _ = [restructure_quantifier(x) for x in quantifier[2] if x != []]

    # We have a child that quantifies no variables, promote its children
    else:

        add_list = []
        for child in quantifier[2]:

            if len(child[1]) == 0:
                add_list += child[2]
                quantifier[2].remove(child)

        quantifier[2] += add_list
        # Since we just promoted children need to re-run on the current node
        restructure_quantifier(quantifier)

def generate_all_axiom(sentences):
    '''
    Utility function which accepts a raw set of axioms and returns a set of
    quantified CNF axioms
    '''

    new_sentences = []

    for sentence in sentences:

        # Skip the import lines
        if sentence[0] == 'cl-imports':
            continue

        print("[+] Sentence:")
        pp.pprint(sentence)

        quantifiers, axiom = Translation.translate_sentence(sentence)
        axioms = extract_conjuncts(axiom[:])

        print("[+] Translated Sentence:")
        pp.pprint(axiom)

        print("------------------")
        for axiom in axioms:
            new_sentences.append(generate_quantifier(axiom, copy.deepcopy(quantifiers)))
            print("[-]  ", new_sentences[-1])

        print("")

    return new_sentences


# Module global set of all extractions
EXTRACTIONS = {extract_disjoint_relation, extract_domain_restriction,
               extract_irreflexive_relation, extract_reflexive_relation,
               extract_subclass_relation, extract_subproperty_relation,
               extract_disjoint_properties, extract_symmetric_relation,
               extract_asymmetric_relation,
               extract_property_range_restriction,
               extract_property_domain_restriction,
               extract_inverted_subproperty_relation,
               extract_functional_relation,
               extract_inverse_functional_relation}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert to OWL!')
    parser.add_argument('-f', '--file', type=str, help='Input Clif', required=True)
    args = parser.parse_args()

    FILE = tempfile.mkstemp(prefix="translation_", dir=TMPDIR)

    clif.remove_all_comments(args.file, FILE[1])
    RAW = clif.get_sentences_from_file(FILE[1])

    print(args.file)
    print('-----------')

    AXIOMS = generate_all_axiom(RAW)

    print('Translations:')
    print('-------------')
    for ax in AXIOMS:

        print('[-]  ', ax)

        quantifier, axiom = ax
        EXT = narrow_translations(axiom, quantifier)

        for ex in EXT:
            if ex(axiom, quantifier) != None:
                print("   [*] ", ex(axiom, quantifier))
