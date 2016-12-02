"""
@Author Robert Powell
@Version 0.0.1

Class that will house the ontology FOL -> OWL stuff
"""

import macleod.Clif as clif
import owlready
import macleod.dl.Translation as translation

def owl_class(class_name, ontology, super_class = owlready.Thing):
    '''
    Dynamically create and return a new OWL class object. If optional
    superclass isn't provided, default to universal OWL Thing.

    :param str class_name, name for the new owl class
    :param onto ontology, ontology for which the class belongs
    :prarm opt str class, default super class for new class
    :return onto class, new OWL class
    '''

    new_class = type(class_name, (super_class,), {'ontology':ontology})

    return new_class

def owl_property(property_name, ontology, super_class = owlready.Property):
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

if __name__ == '__main__':

    import pprint as pp

    sentences = clif.get_sentences_from_file('../../qs/multidim_space_ped/ped.clif_backup')

    unary = set()
    binary = set()

    for s in sentences:
        translated = translation.translate_sentence(s)
        stripped = translation.strip_quantifier(translated)

        unary_predicates = []
        binary_predicates = []

        translation.find_unary_predicates(stripped, unary_predicates)
        translation.find_binary_predicates(stripped, binary_predicates)

        print('-----------')
        pp.pprint(s)
        pp.pprint(translated)
        print(unary_predicates)
        print(binary_predicates)

        for u in unary_predicates:
            unary.add(u[0])

        for b in binary_predicates:
            binary.add(b[0])

    print('=======')

    onto = owlready.Ontology("http://1337.io/onto.owl")

    classes = [owl_class(u, onto) for u in unary]
    properties = [owl_property(b, onto) for b in binary]

    print(onto.classes)
    print(onto.properties)

    print('=======')


    print(owlready.to_owl(onto))
