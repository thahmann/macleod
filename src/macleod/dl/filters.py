"""
Contains several utility methods which serve to quickly filter a set of
possibly applicable Patterns based on the composition of a provided Axiom.

The function you're most likely looking for is the filter_axiom(axiom) method.
"""

import macleod.dl.patterns as Pattern

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

    if len(axiom.existential_quantifiers()) == 0 and len(axiom.universal_quantifiers()) == 1:

        return {Pattern.asymmetric_relation,
                Pattern.disjoint_properties,
                Pattern.disjoint_classes,
                Pattern.domain_restriction,
                Pattern.functional_relation,
                Pattern.inverse_functional_relation,
                Pattern.inverse_subproperty_relation,
                Pattern.irreflexive_relation,
                Pattern.range_restriction,
                Pattern.reflexive_relation,
                Pattern.subclass_relation,
                Pattern.subproperty_relation,
                Pattern.symmetric_relation,
                Pattern.transitive_relation,
                Pattern.universe_restriction,
                Pattern.all_values}

    elif len(axiom.existential_quantifiers()) == 1 and len(axiom.universal_quantifiers()) == 1:
        return {Pattern.some_values}

    elif len(axiom.quantifiers()) == 0:
        return {Pattern.class_assertion,
                Pattern.property_assertion}

    else:
        return set()

def filter_on_variables(axiom):
    """
    Return a set of applicable patterns based on the number of variables in
    the Axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    if len(axiom.variables()) == 0:

        return {Pattern.class_assertion,
                Pattern.property_assertion}


    if len(axiom.variables()) == 1:

        return {Pattern.disjoint_classes,
                Pattern.irreflexive_relation,
                Pattern.reflexive_relation,
                Pattern.subclass_relation,
                Pattern.universe_restriction}

    if len(axiom.variables()) == 2:

        return {Pattern.asymmetric_relation,
                Pattern.disjoint_properties,
                Pattern.domain_restriction,
                Pattern.inverse_subproperty_relation,
                Pattern.range_restriction,
                Pattern.subproperty_relation,
                Pattern.symmetric_relation,
                Pattern.all_values,
                Pattern.some_values}

    if len(axiom.variables()) == 3:

        return {Pattern.functional_relation,
                Pattern.inverse_functional_relation,
                Pattern.subproperty_relation,
                Pattern.transitive_relation}


    return set()

def filter_on_predicates(axiom):
    """
    Returns a set of applicable patterns dependent on the composition of predicate arity
    in the supplied axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    # Axiom is composed of only unary predicates
    if axiom.unary() and not axiom.binary() and not axiom.nary():

        return {Pattern.disjoint_classes,
                Pattern.subclass_relation,
                Pattern.universe_restriction,
                Pattern.class_assertion}

    # Axiom is composed of only binary predicates
    if axiom.binary() and not axiom.unary() and not axiom.nary():

        if len(axiom.binary())==1:
            return {Pattern.irreflexive_relation,
                    Pattern.reflexive_relation,
                    Pattern.property_assertion}

        elif len(axiom.binary()) == 2:
            if len({p.name for p in axiom.predicates()}) == 1:
                # only a single predicate name is used twice
                return {Pattern.asymmetric_relation,
                        Pattern.symmetric_relation,
                        Pattern.property_assertion}
            else:
                return {Pattern.disjoint_properties,
                        Pattern.inverse_subproperty_relation,
                        Pattern.subproperty_relation,
                        Pattern.property_assertion}
        else:
            if len({p.name for p in axiom.predicates()}) == 1:
                return {Pattern.transitive_relation}
            else:
                return {Pattern.disjoint_properties,
                        Pattern.functional_relation,
                        Pattern.inverse_functional_relation,
                        Pattern.inverse_subproperty_relation,
                        Pattern.subproperty_relation,
                        Pattern.property_assertion}

    # Axiom is composed of a mixture of unary and binary predicates
    if axiom.binary() and axiom.unary() and not axiom.nary():
        if len({p.name for p in axiom.binary()}) == 1:
            return {Pattern.domain_restriction,
                    Pattern.range_restriction,
                    Pattern.all_values,
                    Pattern.some_values}

    return set()

def filter_on_sign(axiom):
    """
    Return a set of applicable patterns based on the sign of predicates in
    the Axiom.

    :param Axiom, axiom to filtered
    :return Set patterns, set of applicable patterns
    """

    # Only positive axioms
    if not axiom.negated() and axiom.positive() != 0:

        return {Pattern.reflexive_relation,
                Pattern.universe_restriction,
                Pattern.class_assertion,
                Pattern.property_assertion}

    # Only negative axioms
    if axiom.negated() and not axiom.positive():

        return {Pattern.asymmetric_relation,
                Pattern.domain_restriction,
                Pattern.disjoint_properties,
                Pattern.disjoint_classes,
                Pattern.irreflexive_relation,
                Pattern.range_restriction,
                Pattern.property_assertion}

    # A mixture of axioms
    return {Pattern.domain_restriction,
            Pattern.functional_relation,
            Pattern.inverse_functional_relation,
            Pattern.inverse_subproperty_relation,
            Pattern.range_restriction,
            Pattern.subclass_relation,
            Pattern.subproperty_relation,
            Pattern.symmetric_relation,
            Pattern.transitive_relation,
            Pattern.all_values,
            Pattern.some_values}
