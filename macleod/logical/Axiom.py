"""
Insert boss header here
@RPSkillet
"""

import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol

import copy

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

                    raise ValueError("Look man, 26 axioms is too many")

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
                    raise ValueError("Found a free variable!")

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

    def to_pcnf(self):

        obj = copy.deepcopy(self.sentence)

        def reverse_bfs(root):
            '''
            Conduct a regular BFS over the tree packing each layer into a list
            of [[(term, parent), (term, parent)], ...]

            return that list
            '''

            accumulator = []

            left = [(x, None) for x in root.get_term()]

            while left != []:

                current, parent = left.pop(0)
                accumulator.append((current, parent))

                if not isinstance(current, Symbol.Predicate):

                    # If care about L->R order do reversed(current.get_term())
                    left.extend([(x, current) for x in current.get_term()])

            return reversed(accumulator)

        queue = reverse_bfs(obj)

        # Technically this is our reverse BFS
        for term, parent in queue:

            if isinstance(term, Quantifier.Quantifier):

                # Absorb like-quantifier children
                simplified = term.simplify()

                # Widen scope of nested quantifiers
                broadended = simplified.rescope()

                if not parent is None:

                    parent.remove_term(term)
                    parent.set_term(broadended)

                else:

                    obj = broadended

            elif isinstance(term, Connective.Connective):

                # Quantifier coalescence
                new_term = term.coalesce()

                # Quantifier scoping
                scoped_term = new_term.rescope(parent)

                if not parent is None:

                    parent.remove_term(term)
                    parent.set_term(scoped_term)

                else:

                    obj = scoped_term

        return obj
