"""
Contains Pattern functions which evaluate and break down Axioms
into the needed parts to construct OWL constructs.
"""

from macleod.logical.connective import Conjunction, Disjunction
from macleod.logical.quantifier import Universal, Existential
from macleod.logical.symbol import Predicate
from macleod.logical.negation import Negation
from macleod.dl.owl import Owl


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
    Assumes that all predicates are binary, it's a disjunction, and there exists
    at least one negative term and one positive term. Only a single universally
    quantified variable.
    '''

    # Filter conflict symmetric, need to ensure at least two unique predicates
    #if len({p.name for p in axiom.predicates()}) < 2:
    #    return None
    # More precisely: need to make sure that no predicate occurs in negated and positive form
    positive_names = [p.name for p in axiom.positive()]
    negated_names = [p.name for p in axiom.negated()]

    if len(set(positive_names).intersection(negated_names)) > 0:
        return None

    # gets the first negated predicate (which is binary by assumption)
    base = axiom.negated()[0]
    # compare the variables inside the predicate with the base one: same, inverted or different
    subset = [(s, base.compare(s)) for s in axiom.negated()]
    # the positive predicates become part of the superset
    superset = [(x, base.compare(x)) for x in axiom.positive()]

    # need to check whether any predicate is in the sub- and superset, then this is no subproperty relation

    return ('subproperty', subset, superset)

def disjoint_classes(axiom):
    '''
    Assumes that all predicates are unary, it's a disjunction, and there exists
    only two negated terms. Only a single universally quantified variable.
    '''

    # TODO: Need to handle inverse cases:
    #   this method doesn't currently get called if any positive predicates are present

    # Filter conflict irreflexive, need to ensure at least two unique predicates
    if len({p.name for p in axiom.predicates()}) < 2:
        return None

    # More than one means intersection of terms
    disjoint_classes = [c for c in axiom.unary() if c in axiom.negated()]

    return ('disjoint_classes', disjoint_classes)

def disjoint_properties(axiom):
    '''
    Assumes that all predicates are binary and negated, and there exists
    at least two (negative) terms. Only a single universally quantified variable.
    '''

    # Use of inverse relations in disjoint property statements is not allowed in OWL2

    # Filter conflict asymmetric, need to ensure at least two unique predicates
    if len({p.name for p in axiom.predicates()}) < 2:
        return None

    # More than one means intersection of terms
    base = axiom.negated()[0]
    disjoint_props = [(p, base.compare(p)) for p in axiom.binary() if p in axiom.negated()]

    if all([sign==Predicate.SAME for (_, sign) in disjoint_props]):
        # all predicates need to have the variables in the same order, otherwise an inverse relation is created,
        #  which is not allowed in OWL2
        return ('disjoint_properties', disjoint_props)
    else:
        return None

def reflexive_relation(axiom):
    '''
    Assumes that the predicate is binary and positive and
    only a single universally quantified variable is used.
    '''

    reflexive_property = [p for p in axiom.binary() if p.variables[0]==p.variables[1]]

    if len(reflexive_property)==1:
        return ('reflexive', reflexive_property)
    else:
        return None

def irreflexive_relation(axiom):
    '''
    Assumes that the predicate is binary and negated and
    only a single universally quantified variable is used.
    '''

    irreflexive_property = [p for p in axiom.binary() if p.variables[0]==p.variables[1]]

    if len(irreflexive_property)==1:
        return ('irreflexive', irreflexive_property)
    else:
        return None

def symmetric_relation(axiom):
    '''
    Assume single binary predicate appearing twice, one negated and one not negated. Variables
    should be in reversed positions in each predicate.
    '''

    negated = [p for p in axiom.negated()]
    if len(negated) != 1:
        return None

    positive = [p for p in axiom.positive()]
    if len(positive) != 1:
        return None

    x_one, y_one = negated[0].variables
    x_two, y_two = positive[0].variables
    if x_one==y_two and x_two==y_one:
        return ('symmetric', axiom.binary())
    else:
        return None

def asymmetric_relation(axiom):
    '''
    Assume single binary predicate appearing twice, both negated. Variables
    should be in reversed positions in each predicate.
    '''

    negated = [p for p in axiom.negated()]
    if len(negated) != 2:
        return None

    x_one, y_one = negated[0].variables
    x_two, y_two = negated[1].variables
    if x_one==y_two and x_two==y_one:
        return ('asymmetric', axiom.binary())
    else:
        return None

def transitive_relation(axiom):
    '''
    Assume three universally quantified variable and one predicate appearing 
    three times twice negated.
    '''

    # Ensure we have three properties to define transitive
    properties = [p for p in axiom.binary()]
    if len(properties) != 3:
        return None

    # Ensure a single predicate name is used (already done in filter)
    #if len({p.name for p in axiom.predicates()}) != 1:
    #    return None

    # Ensure the two negated forms appear
    negated = [p for p in axiom.negated()]
    if len(negated) != 2:
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
    Assumes a single binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''

    prop = [p for p in axiom.binary() if p.variables[0]!=p.variables[1] and p in axiom.negated()]
    range_classes_positive = [c for c in axiom.unary() if c not in axiom.negated()]
    range_classes_negative = [c for c in axiom.unary() if c in axiom.negated()]

    if len(prop) != 1:
        return None

    #if len([c for c in axiom.unary() if c in axiom.negated()]) > 1:
    #    return None

    range_var = prop[0].variables[1]
    if not all(map(lambda x: x.variables[0] == range_var, range_classes_positive + range_classes_negative)):
        return None

    return ('range_restriction', prop, range_classes_positive, range_classes_negative)

def domain_restriction(axiom):
    '''
    Assumes a single binary predicate, then an arbitrary of positive
    unary predicates. Only universally quantified predicates are used.
    '''
    
    prop = [p for p in axiom.binary() if p.variables[0]!=p.variables[1] and p in axiom.negated()]
    domain_classes_positive = [c for c in axiom.unary() if c not in axiom.negated()]
    domain_classes_negative = [c for c in axiom.unary() if c in axiom.negated()]

    if len(prop) != 1:
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
    Assumes that the sentence is both universally and existentially quantified.
    Contains exactly two variables.
    Contains a binary and two unary predicates, detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.

    U(a) ^ B(a, b) --> U2(b)

    -U(a) | -B(a, b) | U2(b)


    forall [U subclass B.U2]
    '''

    relation = axiom.binary()

    #print("Checking whether property {} can be used to construct all_values pattern using concepts {}".format(relation, axiom.unary()))

    # Should be a single negated binary, otherwise it is not an AllValuesFrom construct
    if len(relation) != 1 or relation[0] not in axiom.negated():
        return None

    #print("Found property {} for potential all_values pattern using concepts {}".format(relation, axiom.unary()))

    subclass = [(c, c in axiom.negated()) for c in axiom.unary() if c.variables[0] == relation[0].variables[0]]
    limit = [(c, c not in axiom.negated()) for c in axiom.unary() if c.variables[0] == relation[0].variables[1]]

    if not subclass or not limit:
        # empty subclass is covered by the PropertyRange construct
        # empty limit is not meaningful
        return None

    if not all([sign for (_, sign) in subclass]) and all([not sign for (_, sign) in limit]):
            print("Constructing all-values pattern with inverse property {} with subclass {} and limit {}".format(relation[0],subclass, limit))
            # TODO use inverse relation, switch subclass and limit
            return ('all_values',
                    (relation[0], Predicate.INVERTED),
                    [(c, not sign) for (c, sign) in limit],
                    [(c, not sign) for (c, sign) in subclass])
    else:
        return ('all_values', (relation[0], Predicate.SAME), subclass, limit)


def some_values(axiom):
    '''
    Assumes that the sentence is both universally and existentially quantified.
    Contains a single binary and unary predicate(s), detect the placement of the variable
    to see if it's R^(-1).C or Regular R.C.
    '''

    relation = axiom.binary()

    if isinstance(axiom.sentence, Existential):
        # wrong quantifier order
        return None

    nested_term = axiom.sentence.terms[0].terms[0]

    print("Nested term is of kind " + str(type(nested_term)))

    if isinstance(nested_term, Disjunction):
        # case 15: [-R(x,y) | -D(x) v C(y)]
        print("EXPLORING some-values patterns")
        # binary predicate needs to be negated

        negated = [s for s in axiom.unary() if s in axiom.negated()]
        positive = [s for s in axiom.unary() if s not in axiom.negated()]
        # should be at least one subclass and one limit

        if len(negated)>0:
            # Every subclass predicate must be over the same variables
            if not all([s.variables == negated[0].variables for s in negated]):
                return None

        if len(positive)>0:
            # Every limit class must be over the same variables
            if not all([l.variables == positive[0].variables for l in positive]):
                return None

        if relation[0] in axiom.negated():
            if len(negated)>0:
                if negated[0].variables[0] == relation[0].variables[0]:
                    print("FOUND some-values pattern: SubClassOf(ObjectSomeValuesFrom(R, D) C)")
                    return ('some_values', (relation[0], Owl.Relations.NORMAL), negated, positive)
                else:
                    print("FOUND some-values pattern: SubClassOf(ObjectSomeValuesFrom(R, D) C) but variable mismatch")
                    # TODO try the inverse relation
                    return
            else:
                print("FOUND some-values pattern: SubClassOf(ObjectSomeValuesFrom(R, D) C) but D is empty")
                #this is just a domain restrictions
                return
        else:
            if len(positive)==0:
                if negated[0].variables[0] == relation[0].variables[0]:
                    print("FOUND some-values pattern: SubClassOf(C ObjectSomeValuesFrom(R, D)) with empty D")
                    return ('some_values', (relation[0], Owl.Relations.OTHER), positive, negated)
                else:
                    print("FOUND some-values pattern: SubClassOf(C ObjectSomeValuesFrom(R, D)) but variable mismatch")
                    # TODO try the inverse relation
                    return ('some_values', (relation[0], Owl.Relations.INVERSE), positive, negated)

            else:
                print("pattern SubClassOf(C ObjectSomeValuesFrom(R, D)) not applicable here (needs conjunction)")

    else:
        # special case 14 involving a conjunction: [-C(x) v R(x,y)] ^ [-C(x) v D(y)]
        print("NOT YET IMPLEMENTED: some-values pattern SubClassOf(C ObjectSomeValuesFrom(R, D)) with nonempty C and D")
        return
        #
        # # binary predicate cannot be negated
        # if relation in axiom.negated():
        #     return
        #
        # matches = []
        # binary_terms = []
        # for conjunct in nested_term:
        #     # looking just for conjunctions that have exactly two terms in them
        #     if len(conjunct.terms)!=2:
        #         continue
        #     if isinstance(conjunct.terms[0], Predicate) and len(conjunct.terms[0].variables) == 2:
        #         if (isinstance(conjunct.terms[1], Negation) and
        #             isinstance(conjunct.terms[1].terms[0], Predicate) and
        #             len(conjunct.terms[1].terms[0].variables) == 1):
        #             # Found a binary predicate, saving the negated unary one that comes with it
        #             binary_terms.append((conjunct.terms[0],conjunct.terms[1].terms[0]))
        #     elif isinstance(conjunct.terms[1], Predicate) and len(conjunct.terms[1].variables) == 2:
        #         if (isinstance(conjunct.terms[0], Negation) and
        #                 isinstance(conjunct.terms[0].terms[0], Predicate) and
        #                 len(conjunct.terms[0].terms[0].variables) == 1):
        #             # Found a binary predicate, saving the negated unary one that comes with it
        #             binary_terms.append((conjunct.terms[1], conjunct.terms[0].terms[0]))
        #
        # if len(binary_terms)<1:
        #         return
        #
        # for conjunct in nested_term:
        #     # looking just for conjunctions that have exactly two terms in them
        #     if len(conjunct.terms)!=2:
        #         continue
        #     if (isinstance(conjunct.terms[0], Negation) and
        #         isinstance(conjunct.terms[0].terms[0], Predicate) and
        #         len(conjunct.terms[0].terms[0].variables) == 1):
        #         for (b,c) in binary_terms:
        #             # TODO: making sure the negated subclass C matches the prior one
        #             if c.same_symbol(conjunct.terms[0].terms[0]) and c.compare(conjunct.terms[0].terms[0])==Predicate.SAME:
        #                 if isinstance(conjunct.terms[1], Predicate):
        #                     # found a match
        #                     matches.append[(b,c,conjunct.terms[1])]
        #     elif (isinstance(conjunct.terms[1], Negation) and
        #         isinstance(conjunct.terms[1].terms[0], Predicate) and
        #         len(conjunct.terms[1].terms[0].variables) == 1):
        #         for (b,c) in binary_terms:
        #             if c.same_symbol(conjunct.terms[1].terms[0]) and c.compare(conjunct.terms[1].terms[0])==Predicate.SAME:
        #                 if isinstance(conjunct.terms[0], Predicate):
        #                     # found a match
        #                     matches.append[(b,c,conjunct.terms[0])]
        #
        # if len(matches)<1:
        #     if len(binary_terms)>1:
        #         print("Multiple some-values pattern discovered in one axiom -- just using the first one")
        #     # n limit class found, will need to use OWLThing
        #     return ('some_values', binary_terms[0][0], binary_terms[0][1], None)
        # else:
        #     if len(matches)>1:
        #         print("Multiple some-values pattern discovered in one axiom -- just using the first one")
        #     return ('some_values', matches[0][0], matches[0][1], matches[0][2])



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
