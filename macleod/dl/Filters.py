"""
Collection of functions that filter a set of appliable Patterns down based on an
axiom.
"""

import macleod.dl.Patterns as Pattern

def filter_axiom(axiom):
    """
    Returns a set of applicable patterns based on numbers of quantifiers, number of
    variables, types of predicates, and the signs of predicates.

    :param Axiom, axiom to be filtered
    :return Set patterns, set of applicable patterns
    """

    patterns = set(Pattern.PATTERNS)
    patterns &= (filter_on_quantifiers(axiom))
    patterns &= (filter_on_variables(axiom))
    patterns &= (filter_on_predicates(axiom))
    patterns &= (filter_on_sign(axiom))

    return patterns

def filter_on_quantifiers(axiom):
    """
    Return a set of applicable patterns based on the number of quantifiers in
    the Logical.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    if len(axiom.quantifiers()) == 1:

        return {Pattern.inverse_functional_relation, Pattern.subclass_relation,
                Pattern.subproperty_relation, Pattern.functional_relation,
                Pattern.irreflexive_relation, Pattern.reflexive_relation,
                Pattern.inverse_subproperty_relation, Pattern.all_values,
                Pattern.disjoint_properties, Pattern.symmetric_relation,
                Pattern.disjoint_relation, Pattern.universe_restriction,
                Pattern.asymmetric_relation, Pattern.range_restriction}
    else:

        return {Pattern.some_values}

def filter_on_variables(axiom):
    """
    Return a set of applicable patterns based on the number of variables in
    the Axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """


    if len(axiom.variables()) == 1:

        return {Pattern.universe_restriction, Pattern.disjoint_relation,
                Pattern.subclass_relation, Pattern.reflexive_relation,
                Pattern.irreflexive_relation}

    elif len(axiom.variables()) == 2:

        return {Pattern.asymmetric_relation, Pattern.subproperty_relation,
                Pattern.inverse_subproperty_relation, Pattern.all_values,
                Pattern.symmetric_relation, Pattern.range_restriction,
                Pattern.domain_restriction, Pattern.inverse_relation,
                Pattern.some_values}

    elif len(axiom.variables()) == 3:

        return {Pattern.functional_relation, Pattern.inverse_functional_relation}

    else:

        return {}

def filter_on_predicates(axiom):
    """
    Return a set of applicable patterns based on the number of predicates in
    the Axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    if len(axiom.unary()) != 0 and len(axiom.binary()) == 0 and len(axiom.nary()) == 0:

        return {Pattern.universe_restriction, Pattern.disjoint_relation,
                Pattern.subclass_relation, Pattern.some_values}

    elif len(axiom.unary()) == 0 and len(axiom.binary()) != 0 and len(axiom.nary()) == 0:

        return {Pattern.disjoint_properties, Pattern.asymmetric_relation,
                Pattern.subproperty_relation, Pattern.reflexive_relation,
                Pattern.inverse_relation, Pattern.symmetric_relation,
                Pattern.inverse_subproperty_relation}
    else:

        return {Pattern.domain_restriction, Pattern.range_restriction,
                Pattern.some_values, Pattern.all_values}

def filter_on_sign(axiom):
    """
    Return a set of applicable patterns based on the sign of predicates in
    the Axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    if len(axiom.negated()) == 0 and len(axiom.positive()) != 0:

        return {Pattern.universe_restriction, Pattern.reflexive_relation}

    elif len(axiom.negated()) != 0 and len(axiom.positive()) == 0:

        return {Pattern.irreflexive_relation, Pattern.asymmetric_relation,
                Pattern.disjoint_relation, Pattern.disjoint_properties}

    else:

        return {Pattern.subclass_relation, Pattern.subproperty_relation,
                Pattern.domain_restriction, Pattern.range_restriction,
                Pattern.inverse_relation, Pattern.symmetric_relation,
                Pattern.some_values, Pattern.all_values,
                Pattern.inverse_subproperty_relation}
