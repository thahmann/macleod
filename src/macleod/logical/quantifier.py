"""
@author Robert Powell
@version 0.0.2
"""

import copy
import logging

from macleod.logical.logical import Logical
from macleod.logical.symbol import Predicate

LOGGER = logging.getLogger(__name__)

class Quantifier(Logical):

    def __init__(self):

        self.variables = []
        self.terms = []

    def remove_term(self, term):

        self.terms = None

    def set_term(self, term):

        if isinstance(term ,list):
            self.terms = copy.deepcopy(term)
        else:
            self.terms = [term]

    def is_onf(self):
        '''
        A Quantifier can only be in ONF if it is applied to another Quantifier
        and if it's term is in ONF.
        '''

        return self.terms[0].is_onf()

    def to_onf(self):
        '''
        A Quantifier enters ONF by making it's term ONF.

        :return Quantifier, new Quantifier object whose children should be in ONF
        '''

        if self.is_onf():

            return copy.deepcopy(self)

        else:

            new_child = copy.deepcopy(self.terms[0])
            new_child = new_child.to_onf()

            return type(self)(self.variables, [new_child])

    def add_variables(self, variables):

        if not isinstance(variables, list):
            raise ValueError("Variables must be contained in a list")

        for var in variables:
            if not isinstance(var, str):
                raise ValueError("Each variable must be of type str")


        temp = self.variables + copy.deepcopy(variables)
        self.variables += [x for x in temp if x not in self.variables]

        #Only take unique variables -- so assume uniqueness has already been done!
        #self.variables = list(set(self.variables + variables))

    def reduce(self):
        '''
        A pass through which either:
            1. Does nothing if the child is a Symbol or Negation
            2. Calls reduce if its child is a Quantifier
            3. Calls a coalesce + rescope operation if its child is a Connective
        '''

        from macleod.logical.negation import Negation
        from macleod.logical.connective import Connective

        term = self.terms[0]

        if isinstance(term, Predicate) or isinstance(term, Negation):
            return self

        elif isinstance(term, Quantifier):
            self.set_term(term.reduce())
            return self

        else:
            term = term.coalesce()
            if isinstance(term, Quantifier):
                term = term.rescope()
            elif isinstance(term, Connective):
                term = term.rescope(self)
            else:
                raise ValueError("Never again will I choose Ontologies")

            self.set_term(term)
            return self

    def simplify(self):
        '''
        Perform a DFS from a quantifier through it's children to absorb like
        quantifiers. This function is recursive where, upon reaching a
        differently typed Quantifier, it'll restart with the new quantifier as
        the root.
        '''

        ret_object = copy.deepcopy(self)

        def dfs_simplify(current, parent, root):

            # TODO: Really gotta fix this import nonsense
            from macleod.logical.connective import (Conjunction, Disjunction, Connective)

            if parent != current:
                # Quantifier: either Absorb or Reset
                if isinstance(current, Quantifier):

                    if parent != None:

                        if isinstance(current, type(root)):

                            LOGGER.debug("Found a matching quantifier")

                            # Absorb like children
                            root.add_variables(current.variables)
                            parent.remove_term(current)
                            terms = current.get_term()
                            parent.set_term(terms)

                            for term in [x for x in parent.get_term() if not isinstance(x, Predicate)]:
                                dfs_simplify(term, parent, root)

                        else:
                            # Reset our root
                            root = current

            for term in [x for x in current.get_term() if not isinstance(x, Predicate)]:
                dfs_simplify(term, current, root)

        dfs_simplify(ret_object, None, ret_object)

        return ret_object

    def rescope(self):
        '''
        Return a new object that has pulled all quantifiers to the front and
        renamed variables as needed. Must be a B
        '''

        ret_object = copy.deepcopy(self)

        def broaden(symbol, parent, quantifier):

            top_q = quantifier[0]

            if parent is not None:

                if isinstance(symbol, Existential) or isinstance(symbol, Universal):

                    symbol_classname = type(symbol).__name__

                    LOGGER.debug("Quantifier: " + repr(top_q))
                    LOGGER.debug("Symbol: " + repr(symbol))
                    LOGGER.debug("Parent: " + repr(parent))

                    parent.remove_term(symbol)
                    parent.set_term(symbol.get_term())

                    LOGGER.debug("Parent after: " + repr(parent))
                    LOGGER.debug("Symbol after: " + repr(symbol))
                    LOGGER.debug("Quantifier after: " + repr(top_q))

                    #Second version A -- if quantifiers match
                    if isinstance(symbol, type(top_q)):
                        top_q.add_variables(symbol.variables)

                        LOGGER.debug("Broadened Quantifier to parent")
                        LOGGER.debug(repr(top_q))

                    #Second version B -- if quantifiers don't match
                    else:

                        everything = top_q.get_term()
                        new_quantifier = globals()[symbol_classname](symbol.variables, everything)
                        new_quantifier.terms = top_q.get_term()

                        LOGGER.debug("New Quantifier: " + repr(new_quantifier))

                        #Third set upper quantifier to new quantifier
                        top_q.set_term(new_quantifier)
                        quantifier[0] = new_quantifier

                        LOGGER.debug("Reset top quantifier")


        def bfs_broaden(symbol, left):

            quantifier = [symbol]
            seen = set()

            left.append((symbol, None))

            for item in symbol.get_term():
                left.append((item, None))

            while left != []:

                # Need to broaden children who may share quantifier first
                current_parent = left[0][1]
                stack = [x for x in left if (x[1] == current_parent and not isinstance(x, Predicate))]
                for item in stack:
                    if isinstance(item[0], type(quantifier[0])):
                        broaden(item[0], item[1], quantifier)
                        left.remove(item)
                        for term in item[0].get_term():
                            left.append((term, item[0]))
                        stack.remove(item)

                for item_left in stack:
                    broaden(item_left[0], item_left[1], quantifier)
                    left.remove(item_left)
                    if not isinstance(item_left[0], Predicate):
                        for term in [x for x in item_left[0].get_term() if not isinstance(x, Predicate)] :
                            left.append((term, item_left[0]))

        bfs_broaden(ret_object, [])
        return ret_object

    def rename(self, translation):

        obj = copy.deepcopy(self)

        def dfs_rename(current, translation):

            if isinstance(current, Predicate):

                for idx, var in enumerate(current.variables):

                    if var in translation:

                        current.variables[idx] = translation[var]

            else:

                _ = [dfs_rename(x, translation) for x in current.get_term()]

        dfs_rename(obj, translation)
        return obj

    def coalesce(self, other):

        from macleod.logical.connective import (Conjunction, Disjunction, Connective)

        if not isinstance(other, type(self)):
            raise ValueError("Can't coalesce quantifiers of different types {} {}".format(repr(self), repr(other)))

        s = copy.deepcopy(self)
        o = copy.deepcopy(other)

        less, more = (s, o) if len(s.variables) < len(o.variables) else (o, s)
        translation = {old: new for old, new in zip(less.variables, more.variables)}

        less = less.rename(translation)

        terms = less.get_term()
        terms.extend(more.get_term())

        if isinstance(self, Universal):
            ret = type(self)(more.variables, Conjunction(terms))
        else:
            disjunction = Disjunction(terms)
            if len(disjunction.get_term())>0:
                ret = type(self)(more.variables, Disjunction(terms))
            else:
                # empty disjunction
                ret = True

        return ret


class Universal(Quantifier):

    def __init__(self, variables, terms):
        # TODO Allow predicates without names, generate name from class count?

        if isinstance(terms, Logical):

            self.terms = [terms]

        elif isinstance(terms, list):

            if len(terms) != 1:
                raise ValueError('Universal must be over a list of Logical')

            self.terms = copy.deepcopy(terms)

        else:
            raise ValueError('Universal must be over a LogicalObject!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.variables = copy.deepcopy(variables)

    def __repr__(self):

        # problems with unicode characters printing to stdout or a file
        # return "{}({})[{}]".format(u"\u2200", ",".join(self.variables), repr(self.terms[0]))
        return "{}{}\;[{}]".format("\\forall ", ",".join(self.variables), repr(self.terms[0]))


class Existential(Quantifier):

    def __init__(self, variables, terms):

        if isinstance(terms, Logical):

            self.terms = [terms]

        elif isinstance(terms, list):

            if len(terms) != 1:
                raise ValueError('Existential must be over a list of Logical')

            self.terms = copy.deepcopy(terms)

        else:

            print(type(terms))
            raise ValueError('Exi must be over a LogicalObject!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.variables = copy.deepcopy(variables)

    def __repr__(self):

        # problems with unicode characters printing to stdout or a file
        # return "{}({})[{}]".format(u"\u2203", ",".join(self.variables), repr(self.terms[0]))
        return "{}{}\;[{}]".format("\exists ", ",".join(self.variables), repr(self.terms[0]))
