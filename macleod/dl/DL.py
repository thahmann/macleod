"""
@Author Robert Powell
@Version 0.0.1

Class that will house the ontology FOL -> OWL stuff
"""

import argparse
import owlready

import macleod.dl.Extractions as Extractions
import macleod.dl.Translation as Translation

def owl_class(class_name, ontology, super_class=owlready.Thing):
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

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Convert to OWL!')
    parser.add_argument('-f', '--file', type=str, help='Input Clif', required=True)
    args = parser.parse_args()

    axioms, extractions = Extractions.get_all_extractions(args.file)

    unary = set()
    binary = set()

    for a in axioms:

        print (a)
        unary_predicates = []
        binary_predicates = []

        Translation.find_unary_predicates(a[0], unary_predicates)
        Translation.find_binary_predicates(a[0], binary_predicates)


        print('-----------')
        #pp.pprint(s)
        print('')
        #print(is_all_unary(translated[1]))
        #pp.pprint(translated)

        print(unary_predicates)
        print(binary_predicates)

        for u in unary_predicates:
            unary.add(u[0])

        for b in binary_predicates:
            binary.add(b[0])

    print('=======')

    onto = owlready.Ontology("http://1337.io/onto.owl")

    classes = {u: owl_class(u, onto) for u in unary}
    properties = {owl_property(b, onto) for b in binary}

    print(onto.classes)
    print(onto.properties)


    print('=======')


    print(owlready.to_owl(onto))

