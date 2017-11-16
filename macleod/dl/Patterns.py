#!/usr/bin/env python

"""
Collection of functions that accept an Axiom and attempt to identify
any description logic construct that it may contain.
"""

def extract_subclass_relation(axiom, _quantifiers):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    # More than one means intersection of terms
    subset = []
    Translation.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    # More than one means union of terms
    unary = []
    Translation.find_unary_predicates(axiom, unary)
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
    Translation.find_binary_predicates(axiom, clauses)

    if len(clauses) != 3:
        return

    equality = [x for x in clauses if get_predicate_name(x) == EQ]

    if len(equality) != 1:
        return

    negated = []
    Translation.find_negated_predicates(axiom, negated)
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
    Translation.find_binary_predicates(axiom, clauses)

    if len(clauses) != 3:
        return

    equality = [x for x in clauses if get_predicate_name(x) == EQ]

    if len(equality) != 1:
        return

    negated = []
    Translation.find_negated_predicates(axiom, negated)
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
    Translation.find_binary_predicates(axiom, prop)

    classes = []
    Translation.find_unary_predicates(axiom, classes)

    if any([Translation.is_negated(x) for x in classes]):
        return

    if not all([Translation.is_negated(x) for x in prop]):
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
    Translation.find_binary_predicates(axiom, prop)

    classes = []
    Translation.find_unary_predicates(axiom, classes)

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
    Translation.find_binary_predicates(axiom, prop)

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
    Translation.find_binary_predicates(axiom, prop)

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
    Translation.find_negated_predicates(axiom, classes)
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
    Translation.find_negated_predicates(axiom, props)
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
    Translation.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    # More than one means union of terms
    binary = []
    Translation.find_binary_predicates(axiom, binary)
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
    Translation.find_negated_predicates(axiom, subset)
    subset = [Translation.negate_negation(x) for x in subset]

    if len(subset) != 1:
        return

    # More than one means union of terms
    binary = []
    Translation.find_binary_predicates(axiom, binary)
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

def extract_some_partA(axiom, quantifiers):
    '''
    Assumes that the setence is both universally and existentially quantified.
    Contains a binary and unary predicate, detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.
    '''

    binary = []
    Translation.find_binary_predicates(axiom, binary)

    unary = []
    Translation.find_unary_predicates(axiom, unary)

    negated = []
    Translation.find_negated_predicates(axiom, negated)

    # Simplified for now
    # TODO: OWL allows for chained somevalues/allValues from
    if count_clauses(axiom) != 2:
        return

    if Translation.is_negated(negated[0]) != unary[0]:
        return

    universal = []
    existential = []

    for quantifier in quantifiers:
        Translation.get_existentially_quantified(quantifier, existential)
        Translation.get_universally_quantified(quantifier, universal)

    # Need to unary to be universally quantified
    if unary[0][1] not in universal:
        return

    # Need the binary term to be existentially quantified
    if binary[0][1] not in existential and binary[0][2] not in existential:
        return

    property_type = "someValues_A"

    # See if it's an inverse relation or not
    if unary[0][1] == binary[0][2]:
        property_type = "someValues_A_Inverted"

    return (property_type, get_predicate_name(unary[0]),
            get_predicate_name(binary[0]))

def extract_some_partB(axiom, quantifiers):
    '''
    Assumes that the setence is both universally and existentially quantified.
    Contains two and unary predicates, .
    '''

    unary = []
    Translation.find_unary_predicates(axiom, unary)

    negated = []
    Translation.find_negated_predicates(axiom, negated)

    # Simplified for now
    # TODO: OWL allows for chained somevalues/allValues from
    if count_clauses(axiom) != 2:
        return

    universal = []
    existential = []

    for quantifier in quantifiers:
        Translation.get_existentially_quantified(quantifier, existential)
        Translation.get_universally_quantified(quantifier, universal)

    # Need the subclass to be universal
    if Translation.is_negated(negated[0])[1] not in universal:
        return

    restriction = [x for x in unary if Translation.to_negation(x) not in negated]
    # Need the other to be existential
    if restriction[0][1] not in existential:
        return

    property_type = "someValues_B"

    return (property_type, get_predicate_name(Translation.is_negated(negated[0])),
            get_predicate_name(restriction[0]))
