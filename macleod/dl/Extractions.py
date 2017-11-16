#!/usr/bin/env python

"""
Module that processes Logical objects into OWL objects.

Functionality wise this module searches through the Logical objects that
represent first-order logic (FOL) axioms and attempts to identify a suitable
Web Ontology Language (OWL) translation. Not all axioms are guaranteed a
translation and even if an axiom has some valid translation there is no
guarantee that it will be identified. These pattern identification algorithms
are best effort, though in practice they work successfully a majority of the
time.
"""

import argparse
import copy
import functools
import logging
import pprint

import macleod.dl.Translation as Translation

EQ = "="



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


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

def binary_predicates(lst):

    return [i for i in lst if len(i) == 3]

def unary_predicates(lst):

    return [i for i in lst if len(i) == 2]

def positive_predicates(lst):

    return [i for i in lst if not Translation.is_negated(i)]

def negative_predicates(lst):

    return [Translation.is_negated(i) for i in lst if Translation.is_negated(i)]

def single_predicate(lst):

    if len(lst) == 1 and isinstance(lst[0], list):
        return lst.pop()
    else:
        return False

def existential_predicate(predicate, quantifiers):

    if predicate == [] or quantifiers == []:
        return False

    existentials = []
    for quant in quantifiers:
        Translation.get_existentially_quantified(quant, existentials)

    if all([x in existentials for x in predicate[1:]]):
        return predicate
    else:
        return False

def all_existential(lst, q):

    return list(filter(functools.partial(existential_predicate, quantifiers=q), lst))

def universal_predicate(predicate, quantifiers):

    if predicate == [] or quantifiers == []:
        return False

    universals = []
    
    for quant in quantifiers:
        Translation.get_universally_quantified(quant, universals)

    if all([x in universals for x in predicate[1:]]):
        return predicate
    else:
        return False

def all_universal(lst, q):

    rtype = list(filter(functools.partial(universal_predicate, quantifiers=q), lst))


    return rtype

def variable_position(unary, binary):
    '''
    Return whether the unary predicate is scoped over the domain, range, both,
    or none of the variables in the binary predicate. In the caes of none,
    return None. In the case of both, return 3.

    :param list unary, unary predicate
    :param list binary, binary predicate
    :param int/None pos, the position of the scoped variable
    '''

    variable = unary[1]


    if variable == binary[1] and variable == binary[2]:
        return 3
    elif variable in binary:
        return binary.index(variable)
    else:
        return None


def extract_all_values(axiom, quantifiers):
    '''
    Assumes that the setence is both universally and existentially quantified.
    Contains a binary and two unary predicates, detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.

    U(a) ^ B(a, b) --> U2(b)

    -U(a) | -B(a, b) | U2(b)

    forall [U sunclass B.U2]
    '''

    # This extraction requires three clauses -- could be another level of filtering
    if count_clauses(axiom) != 3:
        return

    negated_binary = compose(single_predicate, binary_predicates, negative_predicates)(axiom)

    negated_unary = compose(single_predicate,
                            functools.partial(all_universal, q=quantifiers),
                            unary_predicates,
                            negative_predicates)(axiom)

    positive_unary = compose(single_predicate,
                             functools.partial(all_universal, q=quantifiers),
                             unary_predicates, positive_predicates)(axiom)

    # They all should be assigned, if not then we don't match
    if not all([negated_binary, negated_unary, positive_unary]):
        return

    property_type = "allValues_A"

    # See if it's an inverse relation or not
    if variable_position(negated_unary, negated_binary) == 2:
        property_type = "allValues_A_Inverted"

    return (property_type, get_predicate_name(negated_unary),
            get_predicate_name(negated_binary))

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
    Translation.find_binary_predicates(sentence, predicates)
    Translation.find_unary_predicates(sentence, predicates)
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

        cnf = []

        print("[+] Sentence:")
        pprint.pprint(sentence)

        quantifiers, axiom = Translation.translate_sentence(sentence)
        axioms = extract_conjuncts(axiom[:])

        print("[+] Translated Sentence:")
        pprint.pprint(axiom)

        print("------------------")
        for axiom in axioms:
            cnf.append(generate_quantifier(axiom, copy.deepcopy(quantifiers)))
            print("[-]  ", cnf[-1])

        new_sentences.append((sentence, cnf))
        print("")

    return new_sentences

def generate_all_extractions(sentence):
    '''
    Utility function to return all the OWL extractions from a given sentence.
    Returns a list of extractions.

    :param tuple sentence, ([quantifiers, original], [clausal normal form])
    :return tuple, ([quantifier, sentence], [clausal normal form], [OWL])
    '''

    extractions = []
    original, cnf = sentence

    for conjunct in cnf:

        quantifier, axiom = conjunct
        extractors = narrow_translations(axiom, quantifier)

        for function in extractors:
            if function(axiom, quantifier) != None:
                extractions.append(function(axiom, quantifier))

    return (original, cnf, extractions)

def generate_some_conjunct_extractions(extraction):
    '''
    Utility function which looks over the extractions for a given CNF to
    attempt to pull out patterns which may span multiple conjuncts. This applies
    to allValuesFrom, someValuesFrom, and another whose name is escaping me
    '''

    original, conjunct, extractions = extraction

    some_patterns_one = [(x[1], x[2]) for x in extractions if x[0] == 'someValues_A']
    some_patterns_oneI = [(x[1], x[2]) for x in extractions if x[0] == 'someValues_A_Inverted']
    some_patterns_two = [(x[1], x[2]) for x in extractions if x[0] == 'someValues_B']
    some_patterns_thr = [(x[1], x[2]) for x in extractions if x[0] == 'someValues_C']

    new_pattern = None
    if len(some_patterns_one) != 0:
        new_pattern = ("someValuesFrom", some_patterns_one[0][0],
                       some_patterns_one[0][1])

    if len(some_patterns_oneI) != 0:
        new_pattern = ("someValuesFromInverse", some_patterns_oneI[0][0],
                       some_patterns_oneI[0][1])

    if new_pattern != None and len(some_patterns_two) != 0:
        new_pattern = ("someValuesFrom", some_patterns_one[0][0],
                       some_patterns_one[0][1], some_patterns_two[0][1])

    if new_pattern != None and len(some_patterns_thr) != 0:
        new_pattern = ("someValuesFromEquivalent", some_patterns_one[0][0],
                       some_patterns_one[0][1], some_patterns_two[0][1])

    return new_pattern

#def get_all_extractions(filepath):
#
#    FILE = tempfile.mkstemp(prefix="translation_", dir=TMPDIR)
#
#    clif.remove_all_comments(filepath, FILE[1])
#    RAW = clif.get_sentences_from_file(FILE[1])
#
#    for thing in RAW:
#        pp.pprint(thing)
#
#    print(filepath)
#    print('-----------')
#
#    axioms = generate_all_axiom(RAW)
#
#    print('Translations:')
#    print('-------------')
#
#    for ax in axioms:
#        pp.pprint(ax)
#
#    ext = []
#    for ax in axioms:
#        ext.append(generate_all_extractions(ax))
#
#    extractions = []
#    for e in ext:
#
#        original, clausal, extra = e
#
#        print(original, clausal, extra)
#
#        some_extract = (generate_some_conjunct_extractions(e))
#
#        if some_extract is not None:
#            extra.append(some_extract)
#
#        extractions.append((original, clausal, extra))
#
#
#    return extractions



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
               extract_inverse_functional_relation,
               extract_some_partA,
               extract_some_partB,
               extract_all_values}

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(description='Convert to OWL!')
    PARSER.add_argument('-f', '--file', type=str, help='Input Clif', required=True)
    ARGS = PARSER.parse_args()

    final = get_all_extractions(ARGS.file)
    current = None
    for thing in final:
        o, c, e = thing

        print('[+]', o)
        for item in e:
            print('     [*]', item)
        print()




