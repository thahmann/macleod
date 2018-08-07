"""
Collection of methods that interface with the Owlready2 library to manipulate
OWL2 ontologies
"""

import owlready
import functools
import types

def produce_construct(pattern, ontology):
    """
    Given a pattern tuple instantiate the constuct and add it to an existing
    ontology.

    :param Tuple pattern, pattern that represents a construct
    :param Ontology ontology, owlready.Ontology object
    :return Object construct, otherwise None
    """

    # Figure out which pattern we are working with
    print (pattern)
    if pattern[0] == "subclass":

        # Existing classes
        classes = {str(c):c for c in ontology.classes}

        # Create any missing classes found in the pattern
        for c in pattern[1] + pattern[2]:
            if c.name not in classes:
                klass = owl_class(c.name, ontology)
                classes[c.name] = klass

        subclass = functools.reduce((lambda x ,y : classes[x.name] | classes[y.name]), pattern[1])
        superclass = functools.reduce((lambda x ,y : classes[x.name] | classes[y.name]), pattern[2])

        # Need to create implicit union class
        if len(pattern[2]) > 1:
            # TODO
            pass

        if len(pattern[1]) == 1:
            subclass = classes[subclass.name]

        if len(pattern[2]) == 1:
            superclass = classes[superclass.name]

        print(subclass, superclass)

        subclass.is_a.append(superclass)

    return None



def owl_class(class_name, ontology, super_class=owlready.Thing):
    '''
    Dynamically create and return a new OWL class object. If optional
    superclass isn't provided, default to universal OWL Thing.

    :param str class_name, name for the new owl class
    :param onto ontology, ontology for which the class belongs
    :prarm opt str class, default super class for new class
    :return onto class, new OWL class
    '''

    new_class = types.new_class(class_name, (super_class,), {'ontology':ontology})

    return new_class

def owl_property(property_name, ontology, super_class=owlready.Property):
    '''
    Dynamically create and return a new OWL property class object. If optional
    superclass isn't provided, default to standard owlready Property class.

    :param str property_name, name for the new owl property
    :param onto ontology, ontology for which the property belongs
    :prarm opt str class, default super class for new property
    :return onto property, new OWL class
    '''

    new_prop = type(property_name, (super_class,), {'ontology':ontology})

    return new_prop
