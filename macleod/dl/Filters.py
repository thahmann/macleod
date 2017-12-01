#!/usr/bin/env python

"""
A collection of functions to help refine a collection of 
LogicalObjects against a number of possible translations
"""

import macleod.dl.Patterns as Pattern


def filter_on_quantifiers(sentence, patterns):
    '''
    Reduce the set of possible extractions based on the number of
    quantifiers that a sentence has.

    :param Axiom sentence, axiom to identify patterns in
    :param Set patterns, set of possible patterns
    :return Set patterns, possible set of matching patterns
    '''

    valid_patterns

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

        local_set = {extract_some_partA, extract_some_partB}
        extractions = extractions & local_set

        return filter_on_variables(sentence, quantifiers, extractions)

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
                     extract_property_range_restriction,
                     extract_some_partA, extract_some_partB,
                     extract_all_values}

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

    if Translation.is_all_unary(sentence):

        local_set = {extract_domain_restriction, extract_disjoint_relation,
                     extract_subclass_relation, extract_some_partB}

        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

    elif Translation.is_all_binary(sentence):

        local_set = {extract_disjoint_properties, extract_asymmetric_relation,
                     extract_subproperty_relation,
                     extract_inverted_subproperty_relation,
                     extract_inverse_relation, extract_symmetric_relation,
                     extract_reflexive_relation}

        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

    else:

        local_set = {extract_property_domain_restriction,
                     extract_property_range_restriction,
                     extract_some_partA, extract_all_values}

        extractions = extractions & local_set
        return filter_on_sign(sentence, quantifiers, extractions)

# FOURTH
def filter_on_sign(sentence, _quantifiers, extractions):
    '''
    Filter the number of possible extractions from an axiom based on types of
    predicates signs
    '''

    if Translation.is_all_positive(sentence):

        local_set = {extract_domain_restriction, extract_reflexive_relation}

        extractions = extractions & local_set
        return extractions

    elif Translation.is_all_negative(sentence):

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
                     extract_property_range_restriction,
                     extract_some_partA, extract_some_partB,
                     extract_all_values}

        extractions = extractions & local_set
        return extractions
