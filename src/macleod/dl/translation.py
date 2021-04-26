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

import functools
import logging

import macleod.dl.utilities as Utility
from macleod.dl.owl import Owl
from macleod.logical.symbol import Predicate

LOGGER = logging.getLogger(__name__)

def reset_seen():
    global seen
    seen = set()

def translate_owl(axiom):
    """
    """

    logicals = []
    sentence = axiom.sentence
    Utility.split_logical(sentence, logicals, [], [], [])

    if len(logicals):
        for logical in logicals:
            pruned_logical = Utility.prune_prenex(sentence, logical)
            print(" + yielded: {}".format(str(pruned_logical)))
            yield pruned_logical
    else:
        print(" + yielded: {}".format(str(sentence)))
        yield sentence

def duplicate(pattern):

    global seen

    dup = repr(pattern) in seen
    if dup:
        LOGGER.debug('Duplicate production found: {}... ignoring'.format(repr(pattern)))

    seen.add(repr(pattern))

    return dup


def produce_construct(pattern, ontology):
    """
    Given a pattern tuple instantiate the construct and add it to an existing
    ontology.

    :param Tuple pattern, pattern that represents a construct
    :param Ontology ontology, owlready.Ontology object
    :return Object construct, otherwise None
    """

    # Trim duplicate patterns
    if duplicate(pattern):
        return None

    # Figure out which pattern we are working with
    if pattern[0] == 'subclass':
        return subclass(pattern, ontology)
    elif pattern[0] == 'subproperty':
        return subproperty(pattern, ontology)
    elif pattern[0] == 'disjoint_classes':
        return disjoint_classes(pattern, ontology)
    elif pattern[0] == 'disjoint_properties':
        return disjoint_properties(pattern, ontology)
    elif pattern[0] == 'reflexive':
        return reflexive_property(pattern, ontology)
    elif pattern[0] == 'irreflexive':
        return irreflexive_property(pattern, ontology)
    elif pattern[0] == 'symmetric':
        return symmetric_property(pattern, ontology)
    elif pattern[0] == 'asymmetric':
        return asymmetric_property(pattern, ontology)
    elif pattern[0] == 'transitive':
        return transitive_property(pattern, ontology)
    elif pattern[0] == 'functional':
        return functional_property(pattern, ontology)
    elif pattern[0] == 'inverse-functional':
        return inverse_functional_property(pattern, ontology)
    elif pattern[0] == 'range_restriction':
        return range_restriction(pattern, ontology)
    elif pattern[0] == 'domain_restriction':
        return domain_restriction(pattern, ontology)
    elif pattern[0] == 'all_values':
        return all_values_from(pattern, ontology)
    elif pattern[0] == 'inverse-all_values':
        return inverse_all_values_from(pattern, ontology)
    elif pattern[0] == 'some_values':
        return some_values_from(pattern, ontology)
    elif pattern[0] == 'universe':
        return universe(pattern, ontology)
    elif pattern[0] == 'class-assertion':
        class_assertion(pattern, ontology)
        return None
    elif pattern[0] == 'property-assertion':
        property_assertion(pattern, ontology)
        return None
    elif pattern[0] == 'negative-property-assertion':
        property_assertion(pattern, ontology, negated=True)
        return None

def class_assertion(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    individuals = [*ontology.individuals]

    class_name = pattern[1][0].name
    individual = pattern[1][0].variables[0]

    # Create any missing classes found in the pattern
    ontology.declare_class(class_name)

    if individual not in individuals:
        ontology.declare_individual(individual)
        individuals.append(individual)


    ontology.class_assertion(class_name, individual)

def property_assertion(pattern, ontology, negated=False):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    individuals = [*ontology.individuals]

    property_name = pattern[1][0].name
    individual_one = pattern[1][0].variables[0]
    individual_two = pattern[1][0].variables[1]

    # Create any missing classes found in the pattern
    ontology.declare_property(property_name)

    if individual_one not in individuals:
        ontology.declare_individual(individual_one)
        individuals.append(individual_one)

    if individual_two not in individuals:
        ontology.declare_individual(individual_two)
        individuals.append(individual_two)

    if negated:
        ontology.negative_property_assertion(property_name, (individual_one, individual_two))
    else:
        ontology.property_assertion(property_name, (individual_one, individual_two))

def subclass(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    for c in pattern[1] + pattern[2]:
        ontology.declare_class(c.name)

    subclass = [x.name for x in pattern[1]]
    superclass = [x.name for x in pattern[2]]

    ontology.add_subclass(subclass, superclass)
    return True

def subproperty(pattern, ontology):
    '''
    Extrapolates condensed pattern information to generate Owl ontology constructs.

    First declares any properties that do not already exist in the ontology then
    creates any needed union classes. Keeps track of which properties are inverted and
    passes those along to the ontology object.

    :param tuple(str, [tuple], [tuple]) pattern, tuple which contains sub/super property predicates
    :param Owl ontology, ontology class to add subproperty details
    '''


    # Create any missing properties found in the pattern
    for p, state in pattern[1] + pattern[2]:
        ontology.declare_property(p.name)

    # if more than one property appears on the super side and more than three on the subside, no subproperty axiom can be generated
    # we do not support chains of more than 2 properties
    if len(pattern[1]) > 2 or len(pattern[2]) > 1:
        return None

    sup, state = pattern[2][0]
    superproperty = (sup.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL)

    if len(pattern[1]) == 2:
        # check whether there is a property chain
        sub1, state1 = pattern[1][0]
        sub2, state2 = pattern[1][1]
        chain_vars = []
        if sub1.compare(sub2)==Predicate.CHAIN:
            subproperty = []
            subproperty.append((sub1.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL))
            chain_vars.append(sub1.variables[0])
            subproperty.append((sub2.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL))
            chain_vars.append(sub2.variables[1])
        elif sub2.compare(sub1)==Predicate.CHAIN:
            subproperty = []
            subproperty.append((sub2.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL))
            chain_vars.append(sub2.variables[0])
            subproperty.append((sub1.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL))
            chain_vars.append(sub1.variables[1])
        else:
            return None
        # Finally check whether the variables in the chain match the super variables
        if (chain_vars!=sup.variables):
            return None

    elif len(pattern[1]) == 1:
        sub, state = pattern[1][0]
        subproperty = (sub.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL)

    ontology.add_subproperty(subproperty, superproperty)
    return True



def disjoint_classes(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for c in pattern[1]:
        ontology.declare_class(c.name)

    class_one, class_two = map(lambda x: x.name, pattern[1])

    ontology.add_disjoint_classes((class_one, class_two))
    return True

def disjoint_properties(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing properties found in the pattern
    for p, _ in pattern[1]:
        ontology.declare_property(p.name)

    prop_one, prop_two = map(lambda x: (x[0].name, Owl.Relations.INVERSE if x[1] == Predicate.INVERTED else Owl.Relations.NORMAL), pattern[1])

    ontology.add_disjoint_properties((prop_one, prop_two))
    return True

def reflexive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing properties found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name
    ontology.declare_reflexive_property(prop)
    return True

def irreflexive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing properties found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name
    ontology.declare_irreflexive_property(prop)
    return True

def symmetric_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name

    ontology.declare_symmetric_property(prop)
    return True


def asymmetric_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name

    ontology.declare_asymmetric_property(prop)
    return True

def transitive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name

    ontology.declare_transitive_property(prop)
    return True

def functional_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name

    ontology.declare_functional_property(prop)
    return True


def inverse_functional_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        ontology.declare_property(p.name)

    prop = pattern[1][0].name

    ontology.declare_inverse_functional_property(prop)
    return True


def range_restriction(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    for p in pattern[1]:
        ontology.declare_property(p.name)

    # Create any missing classes found in the pattern
    for c in pattern[2] + pattern[3]:
        ontology.declare_class(c.name)

    property_name = pattern[1][0].name

    if len(pattern[2]) > 1:
        restriction = [(c.name, Owl.Relations.NORMAL) for c in pattern[2]]
        restriction += [(c.name, Owl.Relations.INVERSE) for c in pattern[3]]
    else:
        if pattern[2]:
            restriction = [(pattern[2][0].name, Owl.Relations.NORMAL)]
        elif pattern[3]:
            restriction = [(pattern[3][0].name, Owl.Relations.INVERSE)]

    ontology.declare_range_restriction(property_name, restriction)
    return True


def domain_restriction(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    for p in pattern[1]:
        ontology.declare_property(p.name)

    # Create any missing classes found in the pattern
    for c in pattern[2] + pattern[3]:
        ontology.declare_class(c.name)

    prop = pattern[1][0].name

    if len(pattern[2] + pattern[3]) > 1:
        restriction = [(c.name, Owl.Relations.NORMAL) for c in pattern[2]]
        restriction += [(c.name, Owl.Relations.INVERSE) for c in pattern[3]]
    else:
        if pattern[2]:
            restriction = [(pattern[2][0].name, Owl.Relations.NORMAL)]
        elif pattern[3]:
            restriction = [(pattern[3][0].name, Owl.Relations.INVERSE)]

    ontology.declare_domain_restriction(prop, restriction)
    return True


def all_values_from(pattern, ontology):
    '''
    :param pattern Tuple(str, [], [(predicate, bool)], [(predicate, bool)])
    '''

    _, relation, subclass, limit = pattern
    (relation_name, invert) = relation
    #print("Looking for a all_values pattern involving the property " + property_name)
    ontology.declare_property(relation_name.name)

    for (c, _) in subclass + limit:
        ontology.declare_class(c.name)

    union_classes = []

    for class_list in [subclass, limit]:
        if len(class_list) == 1:
            union_classes.append([(class_list[0][0].name, Owl.Relations.NORMAL if class_list[0][1] else Owl.Relations.INVERSE)])
        else:
            union_classes.append([(c.name, Owl.Relations.NORMAL if sign else Owl.Relations.INVERSE) for (c, sign) in class_list])

    ontology.declare_all_values_from_subclass((relation_name.name,
                                               Owl.Relations.INVERSE if invert == Predicate.INVERTED else Owl.Relations.NORMAL),
                                              union_classes[0], union_classes[1])
    return True


def some_values_from(pattern, ontology):
    '''
    :param pattern Tuple(str, [], [], [])
    '''

    _, relation, subclass, limit = pattern
    (relation_name, negate) = relation
    ontology.declare_property(relation_name.name)

    for c in subclass + limit:
        ontology.declare_class(c.name)

    # Create any union classes for subclass or limit
    union_classes = []
    for class_list in [subclass, limit]:
        if len(class_list) > 1:
            union_class_name = [c.name for c in class_list]
            union_classes.append(union_class_name)
        elif len(class_list)==0:
            union_classes.append([])
        else:
            union_classes.append([class_list[0].name])

    if negate==Owl.Relations.NORMAL or negate==Owl.Relations.INVERSE:
        ontology.declare_some_values_from_subclass(relation, union_classes[0], union_classes[1])
    else:
        ontology.declare_some_values_from_limitclass(relation_name.name, union_classes[1], union_classes[0])

    return True



def universe(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Create any missing classes found in the pattern
    for c in pattern[1]:
        ontology.declare_class(c.name)

    universe_names = [x.name for x in pattern[1]]

    ontology.declare_universe(universe_names)
    return True
