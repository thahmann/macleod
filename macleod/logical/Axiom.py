"""
Insert boss header here
@RPSkillet
"""

import logging

import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Negation as Negation
import macleod.logical.Symbol as Symbol

import copy

LOGGER = logging.getLogger(__name__)

class Axiom(object):
    '''
    Our nice containing object that houses the cool stuff
    '''

    def __init__(self, sentence):

        if not isinstance(sentence, Logical.Logical):
            raise ValueError("Axiom's need Logicals")

        self.sentence = sentence

    def __repr__(self):

        return repr(self.sentence)

    def substitute_functions(self): 
        '''
        Step 1.

        Look through our axiom and replace any functions as necessary. Return
        any additional functional predicates that get created along the way.
        '''

        ret_object = copy.deepcopy(self.sentence)

        # Step 1. Substitute any nested functions!
        def dfs_functions(term, accumulator):

            if isinstance(term, Symbol.Predicate):

                if term.has_functions():

                    clause, axiom = term.substitute_function()
                    accumulator.append(axiom)

                    # May need to repeat a few times!
                    return dfs_functions(clause, accumulator)

                else:

                    return term

            if isinstance(term, Quantifier.Quantifier):

                return type(term)(term.variables, [dfs_functions(x, accumulator) for x in term.get_term()])

            else:

                return type(term)([dfs_functions(x, accumulator) for x in term.get_term()])

        return Axiom(dfs_functions(ret_object, []))

    def standardize_variables(self):
        '''
        Step 2.

        Traverse through our sentence replacing quantifiers so everything is
        unique.
        '''

        ret_object = copy.deepcopy(self.sentence)

        def generator():
            '''
            Go through the alphabet backwards by using ASCII codes. If you run
            out... Complain.
            '''

            start = 122

            def next_term():

                nonlocal start

                character = chr(start)
                start -= 1

                if start == 96:

                    raise ValueError("Look man, 26 variables is just too many. I'm not going to even try")

                return character

            return next_term

        def dfs_standardize(term, gen, translations=[]):

            if isinstance(term, Symbol.Predicate):

                left = len(term.variables)

                for idx, var in enumerate(term.variables):

                    for trans in reversed(translations):

                        if var in trans:

                            term.variables[idx] = trans[var]
                            left -= 1
                            break

                if left != 0:
                    LOGGER.warning("Found a constant!")
                    #raise ValueError("Found a free variable!")

                return term

            elif isinstance(term, Quantifier.Quantifier):

                lookup_table = {}

                for idx, var in enumerate(term.variables):

                    lookup_table[var] = gen()
                    term.variables[idx] = lookup_table[var]

                translations.append(lookup_table)

                return type(term)(term.variables, [dfs_standardize(x, gen, translations) for x in term.get_term()])

            else:

                return type(term)([dfs_standardize(x, gen, translations) for x in term.get_term()])

        return Axiom(dfs_standardize(ret_object, generator(),))

    def push_negation(self):

        new = copy.deepcopy(self.sentence)

        def dfs_negate(term):

            if isinstance(term, Symbol.Predicate):

                return term

            elif isinstance(term, Quantifier.Quantifier):

                return type(term)(term.variables, [dfs_negate(x) for x in term.get_term()])

            elif isinstance(term, Negation.Negation):

                return term.push_complete()

            else:

                return type(term)([dfs_negate(x) for x in term.get_term()])

        return Axiom(dfs_negate(new))

    def to_pcnf(self):

        new = copy.deepcopy(self)
        LOGGER.debug('START ' + repr(new))
        ff = new.substitute_functions()
        LOGGER.debug('FF ' + repr(ff))
        std_var = ff.standardize_variables()
        LOGGER.debug('STD ' + repr(std_var))
        neg = std_var.push_negation()
        LOGGER.debug('NEG ' + repr(neg))
        obj = neg.sentence

        def reverse_bfs(root):
            '''
            Conduct a regular BFS over the tree packing each layer into a list
            of [[(term, parent), (term, parent)], ...]

            return that list
            '''

            accumulator = []

            #left = ([(x, root) for x in root.get_term()])
            left = [(root, None)]

            while left != []:

                current, parent = left.pop(0)
                accumulator.append((current, parent))

                if not isinstance(current, Symbol.Predicate):

                    # If care about L->R order do reversed(current.get_term())
                    left.extend([(x, current) for x in current.get_term()])

            return reversed(accumulator)

        queue = reverse_bfs(obj)
        #for thing in queue:
        #    print(repr(thing))

        # Technically this is our reverse BFS
        for term, parent in queue:

            if isinstance(term, Quantifier.Quantifier):

                LOGGER.debug("Need to work on quantifier now")

                # Absorb like-quantifier children, may require multiple passes
                simplified = term.simplify()
                while True:
                    temp = simplified.simplify()
                    if str(temp) == str(simplified):
                        break
                    else:
                        simplified = temp

                LOGGER.debug("Simplified: " + repr(simplified))

                # Widen scope of nested quantifiers
                broadended = simplified.rescope()
                while True:
                    temp = broadended.rescope()
                    if str(temp) == str(broadended):
                        break
                    else:
                        broadended = temp

                #LOGGER.debug("Broadened: " + repr(broadended))

                if not parent is None:

                    parent.remove_term(term)
                    #parent.set_term(simplified)
                    parent.set_term(broadended)

                else:

                    #obj = simplified
                    obj = broadended

            elif isinstance(term, Connective.Connective):

                # Quantifier coalescence
                LOGGER.debug('PRE-CSX ' + repr(term))
                new_term = term.coalesce()

                # Quantifier scoping
                LOGGER.debug('CSX ' + repr(new_term))

                if not isinstance(new_term, Quantifier.Quantifier):
                    LOGGER.debug('Rescoping returned connective')
                    scoped_term = new_term.rescope(parent)
                else:
                    LOGGER.debug('Rescoping returned quantifier')
                    scoped_term = new_term.rescope()


                if not parent is None:

                    parent.remove_term(term)
                    parent.set_term(scoped_term)

                else:

                    obj = scoped_term

        LOGGER.debug('SCP ' + repr(obj))

        onf_obj = obj.to_onf()
        current = repr(onf_obj)


        history = [onf_obj]
        while current != repr(history[-1].to_onf()):
            LOGGER.debug("Looping again for onf " + repr(onf_obj))
            history.append(history[-1].to_onf)
            current = repr(history[-1])

        LOGGER.debug('FF-PCNF ' + repr(onf_obj))

        return Axiom(onf_obj)
