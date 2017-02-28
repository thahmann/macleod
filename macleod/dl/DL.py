"""
@Author Robert Powell
@Version 0.0.1

Class that will house the ontology FOL -> OWL stuff
"""

import macleod.Clif as clif
import macleod.dl.Translation as Translation
import owlready

import tempfile


def is_all_universal(quantifiers):
    '''
    Checks if all quantifiers used are universal

    :param list quantifiers
    :return boolean result
    '''

    result = True

    for quantifier in quantifiers:

        result &= Translation.is_universal(quantifier)

    return result

def is_all_existential(quantifiers):
    '''
    Checks if all quantifiers used are existential

    :param list quantifiers
    :return boolean result
    '''
    result = True

    for quantifier in quantifiers:

        result &= Translation.is_existential(quantifier)

    return result

def is_all_unary(sentence):
    '''
    Checks to see if all predicates in sentence are unary.

    :param list sentence, FOL sentence
    :return boolean
    '''

    result = True

    if Translation.is_disjunction(sentence):
        terms = Translation.is_disjunction(sentence)
    elif Translation.is_conjunction(sentence):
        terms = Translation.is_conjunction(sentence)

    else:
        terms = sentence

    for term in terms:

        if Translation.is_negated(term):
            result &= Translation.is_unary(term[1])
        else:
            result &= Translation.is_unary(term)

    return result

def is_all_binary(sentence):
    '''
    Checks to see if all predicates in sentence are binary.

    :param list sentence, FOL sentence
    :return boolean
    '''

    result = True

    if Translation.is_disjunction(sentence):
        terms = Translation.is_disjunction(sentence)

    elif Translation.is_conjunction(sentence):
        terms = Translation.is_conjunction(sentence)

    else:
        terms = sentence

    for term in terms:

        if Translation.is_negated(term):
            result &= Translation.is_binary(term[1])
        else:
            result &= Translation.is_binary(term)

    return result

def is_all_positive(sentence):
    '''
    Checks to see if all predicates in sentence are not negated.

    :param list sentence, FOL sentence
    :return boolean
    '''

    result = True

    for term in sentence:
        if Translation.is_negated(term):
            return False

    return result

def is_all_negative(sentence):
    '''
    Checks to see if all predicates in sentence are not negated.

    :param list sentence, FOL sentence
    :return boolean
    '''

    result = True

    for term in sentence:
        if term != 'or' and term != 'and' and not Translation.is_negated(term):
            return False

    return result

def find_unary_predicates(sentence, predicates):
    '''
    Given a FOL setence, extract all nonlogical symbols that have arity 1.

    :param list sentence, input FOL sentence
    :param list predicates, accumulator for found unary predicates
    '''

    if not isinstance(sentence, list):
        return None

    #sentence = Translation.strip_quantifier(sentence)

    for sub_sentence in sentence:

        if Translation.is_unary(sub_sentence):
            predicates.append(sub_sentence)
        else:
            find_unary_predicates(sub_sentence, predicates)

def find_binary_predicates(sentence, predicates):
    '''
    Given a FOL setence, extract all nonlogical symbols that have arity 1.

    :param list sentence, input FOL sentence
    :param list predicates, accumulator for found unary predicates
    '''

    if not isinstance(sentence, list):
        return None

    #sentence = Translation.strip_quantifier(sentence)

    for sub_sentence in sentence:

        if Translation.is_binary(sub_sentence):
            predicates.append(sub_sentence)
        else:
            find_binary_predicates(sub_sentence, predicates)

def find_negated_predicates(sentence, predicates):
    '''
    Given a FOL setence, extract all nonlogical symbols that are negated.

    :param list sentence, input FOL sentence
    :param list predicates, accumulator for found unary predicates
    '''

    if not isinstance(sentence, list):
        return None

    #sentence = Translation.strip_quantifier(sentence)

    for sub_sentence in sentence:

        if Translation.is_negated(sub_sentence):
            predicates.append(sub_sentence)
        else:
            find_negated_predicates(sub_sentence, predicates)


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
        translated = Translation.translate_sentence(s)

        unary_predicates = []
        binary_predicates = []

        find_unary_predicates(translated[1], unary_predicates)
        find_binary_predicates(translated[1], binary_predicates)

        print('-----------')
        #pp.pprint(s)
        print('')
        print(is_all_unary(translated[1]))
        pp.pprint(translated)

        #print(unary_predicates)
        #print(binary_predicates)

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

    sup = classes.pop()
    sup_two = classes.pop()

    class nup(owlready.Thing):
        ontology = onto
        equivalent_to = [sup | sup_two]

    print("LDKJFLDSKFJLSDKFJLSDKFJ")
    for c in classes:
        c.is_a = [sup | sup_two]

    for d in onto.subclasses_of(nup):
        print (d)

    print('=======')


    print(owlready.to_owl(onto))

