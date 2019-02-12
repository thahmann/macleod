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

import macleod.dl.Utilities as Utility
from macleod.dl.owl import Owl
from macleod.logical.symbol import Predicate

LOGGER = logging.getLogger(__name__)

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

def duplicate(pattern, seen=set()):

    dup = repr(pattern) in seen
    if dup:
        LOGGER.debug('Duplicate production found: {}... ignoring'.format(repr(pattern)))

    seen.add(repr(pattern))

    return dup


def produce_construct(pattern, ontology):
    """
    Given a pattern tuple instantiate the constuct and add it to an existing
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
        subclass(pattern, ontology)
    elif pattern[0] == 'subproperty':
        subproperty(pattern, ontology)
    elif pattern[0] == 'disjoint_classes':
        disjoint_classes(pattern, ontology)
    elif pattern[0] == 'disjoint_properties':
        disjoint_properties(pattern, ontology)
    elif pattern[0] == 'reflexive':
        reflexive_property(pattern, ontology)
    elif pattern[0] == 'irreflexive':
        reflexive_property(pattern, ontology)
    elif pattern[0] == 'symmetric':
        symmetric_property(pattern, ontology)
    elif pattern[0] == 'asymmetric':
        asymmetric_property(pattern, ontology)
    elif pattern[0] == 'transitive':
        transitive_property(pattern, ontology)
    elif pattern[0] == 'functional':
        functional_property(pattern, ontology)
    elif pattern[0] == 'inverse-functional':
        inverse_functional_property(pattern, ontology)
    elif pattern[0] == 'range_restriction':
        range_restriction(pattern, ontology)
    elif pattern[0] == 'domain_restriction':
        domain_restriction(pattern, ontology)
    elif pattern[0] == 'all_values':
        all_values_from(pattern, ontology)
    elif pattern[0] == 'some_values':
        some_values_from(pattern, ontology)
    elif pattern[0] == 'universe':
        universe(pattern, ontology)
    elif pattern[0] == 'class-assertion':
        class_assertion(pattern, ontology)
    elif pattern[0] == 'property-assertion':
        property_assertion(pattern, ontology)
    elif pattern[0] == 'negative-property-assertion':
        property_assertion(pattern, ontology, negated=True)

def class_assertion(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    classes = [*ontology.classes]
    individuals = [*ontology.individuals]

    class_name = pattern[1][0].name
    individual = pattern[1][0].variables[0]

    # Create any missing classes found in the pattern
    if class_name not in classes:
        ontology.declare_class(class_name)
        classes.append(class_name)

    if individual not in individuals:
        ontology.declare_individual(individual)
        individuals.append(individual)


    ontology.class_assertion(class_name, individual)

def property_assertion(pattern, ontology, negated=False):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]
    individuals = [*ontology.individuals]

    property_name = pattern[1][0].name
    individual_one = pattern[1][0].variables[0]
    individual_two = pattern[1][0].variables[1]

    # Create any missing classes found in the pattern
    if property_name not in properties:
        ontology.declare_property(property_name)
        properties.append(property_name)

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

    # Existing classes
    classes = [*ontology.classes]

    # Create any missing classes found in the pattern
    for c in pattern[1] + pattern[2]:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

    subclass = [x.name for x in pattern[1]]
    superclass = [x.name for x in pattern[2]]

    ontology.add_subclass(subclass, superclass)

def subproperty(pattern, ontology):
    '''
    Extrapolates condensed pattern information to generate Owl ontology constructs.

    First declares any properties that do not already exist in the ontology then
    creates any needed union classes. Keeps track of which properties are inverted and
    passes those along to the ontology object.

    :param tuple(str, [tuple], [tuple]) pattern, tuple which contains sub/super property predicates
    :param Owl ontology, ontology class to add subproperty details
    '''

    # Existing properties
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p, state in pattern[1] + pattern[2]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)


    # Need to create implicit union class
    if len(pattern[1]) > 1:
        return None

    if len(pattern[2]) > 1:
        return None

    if len(pattern[1]) == 1:
        sub, state = pattern[1][0]
        subproperty = (sub.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL)
    else:
        subproperty = (union_subproperty_name, Owl.Relations.NORMAL)

    if len(pattern[2]) == 1:
        sup, state = pattern[2][0]
        superproperty = (sup.name, Owl.Relations.INVERSE if state == Predicate.INVERTED else Owl.Relations.NORMAL)
    else:
        superproperty = (union_property_name, Owl.Relations.NORMAL)

    ontology.add_subproperty(subproperty, superproperty)

def disjoint_classes(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    classes = [*ontology.classes]

    # Create any missing classes found in the pattern
    for c in pattern[1]:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

    class_one, class_two = map(lambda x: x.name, pattern[1])

    ontology.add_disjoint_classes((class_one, class_two))

def disjoint_properties(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p, _ in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop_one, prop_two = map(lambda x: (x[0].name, Owl.Relations.INVERSE if x[1] == Predicate.INVERTED else Owl.Relations.NORMAL), pattern[1])

    ontology.add_disjoint_properties((prop_one, prop_two))

def reflexive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = map(lambda x: x.name, pattern[1])

    ontology.declare_reflexive_property(prop)

def irreflexive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = map(lambda x: x.name, pattern[1])

    ontology.declare_irreflexive_property(prop)

def symmetric_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = pattern[1][0].name

    ontology.declare_symmetric_property(prop)

def asymmetric_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = pattern[1][0].name

    ontology.declare_asymmetric_property(prop)

def transitive_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = pattern[1][0].name

    ontology.declare_transitive_property(prop)

def functional_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = pattern[1][0].name

    ontology.declare_functional_property(prop)

def inverse_functional_property(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    properties = [*ontology.properties]

    # Create any missing classes found in the pattern
    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    prop = pattern[1][0].name

    ontology.declare_inverse_functional_property(prop)

def range_restriction(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    classes = [*ontology.classes]
    properties = [*ontology.properties]

    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    # Create any missing classes found in the pattern
    for c in pattern[2] + pattern[3]:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

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

def domain_restriction(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    classes = [*ontology.classes]
    properties = [*ontology.properties]

    for p in pattern[1]:
        if p.name not in properties:
            ontology.declare_property(p.name)
            properties.append(p.name)

    # Create any missing classes found in the pattern
    for c in pattern[2] + pattern[3]:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

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

def all_values_from(pattern, ontology):
    '''
    :param pattern Tuple(str, [], [], [])
    '''

    # Existing classes
    classes = [*ontology.classes]
    properties = [*ontology.properties]

    _, relation, subclass, limit = pattern
    property_name = relation[0].name

    # Ensure that properties and classes already exist 
    if property_name not in properties:
        ontology.declare_property(property_name)
        properties.append(property_name)

    for c in subclass + limit:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

    # Create any union classes for subclass or limit
    union_classes = []
    for class_list in [subclass, limit]:
        if len(class_list) > 1:
            union_class_name = [c.name for c in class_list]
            union_classes.append(union_class_name)
        else:
            union_classes.append(None)

    subclass_name = union_classes[0] or [subclass[0].name]
    limit_name = union_classes[1] or [limit[0].name]

    ontology.declare_all_values_from_subclass(property_name, subclass_name, limit_name)

def some_values_from(pattern, ontology):
    '''
    :param pattern Tuple(str, [], [], [])
    '''

    # Existing classes
    classes = [*ontology.classes]
    properties = [*ontology.properties]

    _, relation, subclass, limit = pattern
    property_name = relation[0].name

    # Ensure that properties and classes already exist 
    if property_name not in properties:
        ontology.declare_property(property_name)
        properties.append(property_name)

    for c in subclass + limit:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

    # Create any union classes for subclass or limit
    union_classes = []
    for class_list in [subclass, limit]:
        if len(class_list) > 1:
            union_class_name = [c.name for c in class_list]
            union_classes.append(union_class_name)
        else:
            union_classes.append(None)

    subclass_name = union_classes[0] or [subclass[0].name]
    limit_name = union_classes[1] or [limit[0].name]

    ontology.declare_some_values_from_subclass(property_name, subclass_name, limit_name)

def universe(pattern, ontology):
    '''
    TODO: Actually write these
    '''

    # Existing classes
    classes = [*ontology.classes]

    # Create any missing classes found in the pattern
    for c in pattern[1]:
        if c.name not in classes:
            ontology.declare_class(c.name)
            classes.append(c.name)

    universe_names = [x.name for x in pattern[1]]

    ontology.declare_universe(universe_names)
