"""
Contains Pattern functions which evaluate and break down Axioms
into the needed parts to construct OWL constructs.
"""

from macleod.logical.connective import Conjunction
from macleod.logical.quantifier import Universal
from macleod.logical.symbol import Predicate
from macleod.logical.negation import Negation


EQUALITY = '='


def subclass_relation(axiom):
    """
    Identifies a subclass relation axiom. Expects a single variable and all
    variables to be universally quantified and all predicates unary. There must
    exist at least two predicates and at least one negated predicate.

    :param Axiom axiom, the axiom to search for a subclass relation in
    :return tuple pattern, if pattern applicable return a tuple otherwise None
    """

    subset = [e for e in axiom.unary() if e in axiom.negated()]
    superset = [x for x in axiom.unary() if x not in subset]

    if subset and superset:
        return ('subclass', subset, superset)

    return None

def inverse_subproperty_relation(axiom):
    '''
    Pass through for subproperty_relation
    '''

    return subproperty_relation(axiom)

def subproperty_relation(axiom):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    # Filter conflict symmetric, need to ensure at least two unique predicates
    if len({p.name for p in axiom.predicates()}) < 2:
        return None

    base = axiom.negated()[0]
    subset = [(s, base.compare(s)) for s in axiom.negated()]
    superset = [(x, base.compare(x)) for x in axiom.binary() if x not in [y[0] for y in subset]]

    return ('subproperty', subset, superset)

def disjoint_classes(axiom):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    only two negated terms. Only a single universally quantified variable.
    '''

    # TODO: Need to handle inverse cases

    # Filter conflict irreflexive, need to ensure at least two unique predicates
    if len({p.name for p in axiom.predicates()}) < 2:
        return None

    # More than one means intersection of terms
    disjoint_classes = [c for c in axiom.unary() if c in axiom.negated()]

    return ('disjoint_classes', disjoint_classes)

def disjoint_properties(axiom):
    '''
    Assumes that all predicates are binary, it's a disjunction, and there exists
    at least two negative terms. Only a single universally quantified variable.
    '''

    # TODO: Need to handle inverse cases

    # Filter conflict asymmetric, need to ensure at least two unique predicates
    if len({p.name for p in axiom.predicates()}) < 2:
        return None

    # More than one means intersection of terms
    base = axiom.negated()[0]
    disjoint_props = [(p, base.compare(p)) for p in axiom.binary() if p in axiom.negated()]

    return ('disjoint_properties', disjoint_props)

def reflexive_relation(axiom):
    '''
    Assumes that the predicate is binary and only a single universally
    quantified variable is used.
    '''

    # TODO: Add extra check to ensure only reflexive
    reflexive_property = [p for p in axiom.binary()]

    return ('reflexive', reflexive_property)

def irreflexive_relation(axiom):
    '''
    Assumes that the predicate is binary and only a single universally
    quantified variable is used.
    '''

    # Filter conflict disjoint, need a single predicate
    if len({p.name for p in axiom.predicates()}) == 1:
        return None

    # TODO: Add extra check to ensure only reflexive
    irreflexive_property = [p for p in axiom.binary()]

    return ('irreflexive', irreflexive_property)

def symmetric_relation(axiom):
    '''
    Assume single binary predicate appearing twice, one negated and one not negated. Variables
    should be in reversed positions in each predicate.
    '''

    # TODO: Check for inverse

    # Filter conflict disjoint subproperty, need a single predicate
    if len({p.name for p in axiom.predicates()}) != 1:
        return None

    return ('symmetric', axiom.binary())

def asymmetric_relation(axiom):
    '''
    Assume single binary predicate appearing twice, both negated. Variables
    should be in reversed positions in each predicate.
    '''

    # TODO: Check for inverse

    # Filter conflict disjoint property, need a single predicate
    if len({p.name for p in axiom.predicates()}) != 1:
        return None

    return ('asymmetric', axiom.binary())

def transitive_relation(axiom):
    '''
    Assume three universally quantified variable and one predicate appearing 
    three times twice negated.
    '''

    # Filter conflict functional property, need a three predicates
    if len({p.name for p in axiom.predicates()}) != 3:
        return None

    # Ensure we have three properties to define transitive
    properties = [p for p in axiom.binary()]
    if len(properties) != 3:
        return None

    # Ensure the two negated forms appear
    negated = [p for p in axiom.negated()]
    if len(negated) != 2:
        return None

    # Ensure the three properties are all the same
    name = properties[0].name
    if not all([x.name == name for x in properties]):
        return None

    # Follow the rainbow for the transitive
    x_one, y_one = negated[0].variables
    x_two, y_two = negated[1].variables

    if y_one == x_two:
        x = x_one
        z = y_two
    elif x_two == y_one:
        x = x_two
        z = y_one
    else:
        return None

    positive_x, positive_z = axiom.positive()[0].variables
    if positive_x != x or positive_z != z:
        return None

    return ('transitive', [axiom.positive()[0]])

def range_restriction(axiom):
    '''
    Assumes a single negated binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''
    
    prop = [p for p in axiom.binary()]
    range_classes_positive = [c for c in axiom.unary() if c not in axiom.negated()]
    range_classes_negative = [c for c in axiom.unary() if c in axiom.negated()]

    if len(prop) > 1:
        return None

    #if len([c for c in axiom.unary() if c in axiom.negated()]) > 1:
    #    return None

    range_var = prop[0].variables[1]
    if not all(map(lambda x: x.variables[0] == range_var, range_classes_positive + range_classes_negative)):
        return None

    return ('range_restriction', prop, range_classes_positive, range_classes_negative)

def domain_restriction(axiom):
    '''
    Assumes a single negated binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''
    
    prop = [p for p in axiom.binary()]
    domain_classes_positive = [c for c in axiom.unary() if c not in axiom.negated()]
    domain_classes_negative = [c for c in axiom.unary() if c in axiom.negated()]

    if len(prop) > 1:
        return None

    #if len([c for c in axiom.unary() if c in axiom.negated()]) > 1:
    #    return None

    domain_var = prop[0].variables[0]
    if not all(map(lambda x: x.variables[0] == domain_var, domain_classes_positive + domain_classes_negative)):
        return None

    return ('domain_restriction', prop, domain_classes_positive, domain_classes_negative)

def inverse_functional_relation(axiom):
    '''
    Pass through for functional relation
    '''

    result = functional(axiom)
    return result if result and result[0] == 'inverse-functional' else None

def functional_relation(axiom):
    '''
    Pass through for functional tester
    '''

    result = functional(axiom)
    return result if result and result[0] == 'functional' else None

def functional(axiom):
    '''
    Assumes two predicates, one of which is the Equality predicate. The
    non-equality predicate is negated and appears twice. Both instances will
    share the same variable for domain, but different variable for range. One
    predicate will share domain with equality, the other will share range with
    equality.
    '''

    # Filter conflict transitive property, need two unique predicates including equality
    if len({p.name for p in axiom.predicates()}) != 2:
        return None

    # Need exactly three predicates
    if len([p for p in axiom.predicates()]) != 3:
        return None

    # Functional relation must contain single non-negated equality
    if all([p.name != EQUALITY for p in axiom.predicates() if p not in axiom.negated()]):
        return None

    equality = [p for p in axiom.binary() if p not in axiom.negated()].pop()
    negated_one, negated_two = axiom.negated()
    if negated_one.variables[0] == negated_two.variables[0]:
        inverse = False
    elif negated_one.variables[1] == negated_two.variables[1]:
        inverse = True
    else:
        return None

    # TODO: Find a more concise way to express this
    if not inverse:
        if equality.variables[0] == negated_one.variables[1] and equality.variables[1] == negated_two.variables[1]:
            pass
        elif equality.variables[0] == negated_two.variables[1] and equality.variables[1] == negated_one.variables[1]:
            pass
        else:
            return None
        return ('functional', [e for e in axiom.negated()])
    else:
        if equality.variables[0] == negated_one.variables[0] and equality.variables[1] == negated_two.variables[0]:
            pass
        elif equality.variables[0] == negated_two.variables[0] and equality.variables[1] == negated_one.variables[0]:
            pass
        else:
            return None
        return ('inverse-functional', [e for e in axiom.negated()])

def all_values(axiom):
    '''
    Assumes that the setence is both universally and existentially quantified.
    Contains a binary and two unary predicates, detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.

    U(a) ^ B(a, b) --> U2(b)

    -U(a) | -B(a, b) | U2(b)

    forall [U subclass B.U2]
    '''

    relation = axiom.binary()
    subclass = [s for s in axiom.unary() if s in axiom.negated()]
    limit = [s for s in axiom.unary() if s not in axiom.negated()]

    # Should be a single binary
    if not relation or len(relation) > 1:
        return None

    # Should be at least one subclass
    if not subclass:
        return None

    # Every subclass predicate must be over the same variables
    if not all([s.variables == subclass[0].variables for s in subclass]):
        return None

    # Should be at least one limiting class
    if not limit:
        return None

    # Every limit class must be over the same variables
    if not all([l.variables == limit[0].variables for l in limit]):
        return None

    return ('all_values', relation, subclass, limit)

def some_values(axiom):
    '''
    Assumes that the setence is both universally and existentially quantified.
    Contains a binary and unary predicate, detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.
    '''

    if not isinstance(axiom.sentence.terms[0], Conjunction):
        return None

    relation = axiom.binary()
    subclass = [s for s in axiom.unary() if s in axiom.negated()]
    limit = [s for s in axiom.unary() if s not in axiom.negated()]

    # Should be a single binary
    if not relation or len(relation) > 1:
        return None

    # Should be at least one subclass
    if not subclass:
        return None

    # Every subclass predicate must be over the same variables
    if not all([s.variables == subclass[0].variables for s in subclass]):
        return None

    # Should be at least one limiting class
    if not limit:
        return None

    # Every limit class must be over the same variables
    if not all([l.variables == limit[0].variables for l in limit]):
        return None

    return ('some_values', relation, [subclass[0]], [limit[0]])


def universe_restriction(axiom):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    if not isinstance(axiom.quantifiers()[0], Universal):
        return None

    return ('universe', axiom.unary())

def class_assertion(axiom):
    '''
    Expects an axiom with no quantifiers, single unary predicate, and constant.

    :param logical.Axiom axiom, axiom containing the class assertion
    :returns Axiom, l
    '''

    if axiom.quantifiers() or axiom.binary() or axiom.nary():
        return None

    if not isinstance(axiom.sentence, Predicate):
        return None

    if len(axiom.unary()) != 1:
        return None

    return ('class-assertion', axiom.unary())

def property_assertion(axiom):
    '''
    Expects an axiom with no quantifiers, single binary predicate, and two constants.

    :param logical.Axiom axiom, axiom containing the class assertion
    :returns Axiom, l
    '''

    if axiom.quantifiers() or axiom.unary() or axiom.nary():
        return None

    if len(axiom.binary()) != 1:
        return None

    if not isinstance(axiom.sentence, Predicate):
        if not isinstance(axiom.sentence, Negation):
            return None

        return ('negative-property-assertion', axiom.binary())


    return ('property-assertion', axiom.binary())


PATTERNS = frozenset([all_values,
                      asymmetric_relation,
                      disjoint_classes,
                      disjoint_properties,
                      domain_restriction,
                      functional_relation,
                      inverse_functional_relation,
                      irreflexive_relation,
                      range_restriction,
                      reflexive_relation,
                      some_values,
                      subclass_relation,
                      subproperty_relation, # Also covers inverse subproperty
                      symmetric_relation,
                      transitive_relation,
                      universe_restriction,
                      class_assertion,
                      property_assertion])
