"""
@author Robert Powell
@version 0.0.2
"""

from macleod.logical.logical import Logical
from macleod.logical.connective import (Conjunction, Disjunction, Connective)
from macleod.logical.symbol import (Function, Predicate)
from macleod.logical.quantifier import (Universal, Existential, Quantifier)

import copy

class Negation(Logical):
    '''
    Representation of a negation to wrap Predicates, Disjunctions, and
    Conjunctions and Quantifiers.
    '''

    def __init__(self, terms):

        if isinstance(terms, list):
            if len(terms) != 1:
                raise ValueError("Must apply negation to a single element")

            term = copy.deepcopy(terms.pop())
            self.terms = [term]

        elif isinstance(terms, Logical):

            self.terms = [copy.deepcopy(terms)]

        else:

            raise ValueError("Negation not init'd right")

    def set_term(self, terms):

        if isinstance(terms, list):
            if len(terms) != 1:
                raise ValueError("Must apply negation to a single element")

            term = copy.deepcopy(terms.pop())
            self.terms = [term]

        elif isinstance(terms, Logical):

            self.terms = [copy.deepcopy(terms)]

        else:

            raise ValueError("Negation must be passed a list or Logical")

    def term(self):

        return copy.deepcopy(self.terms[0])

    def is_negation_of(self, other):

        if isinstance(other, Negation):
            return False

        if not isinstance(other, Predicate):
            return False

        if not isinstance(self.term(), Predicate):
            return False

        if self.term().same_symbol(other):
            if self.term().compare(other)==Predicate.SAME:
                return True

        return False

    def push(self):
        '''
        Push negation inwards and apply to all children
        '''

        # Can be a conjunction or disjunction
        # Can be a single predicate
        # Can be a quantifier

        if isinstance(self.term(), Conjunction):

            ret = Disjunction([Negation(x) for x in self.term().get_term()])

        elif isinstance(self.term(), Disjunction):

            ret = Conjunction([Negation(x) for x in self.term().get_term()])

        elif isinstance(self.term(), Predicate):

            ret = self

        elif isinstance(self.term(), Existential):

            ret = Universal(self.term().variables, Negation(self.term().get_term()))

        elif isinstance(self.term(), Universal):

            ret = Existential(self.term().variables, Negation(self.term().get_term()))

        elif isinstance(self.term(), Negation):

            ret = self.term().term()

        else:

            raise ValueError("Negation onto unknown type!", self.term)

        return copy.deepcopy(ret)

    def push_complete(self):
        '''
        Push a negation as deeply as possible
        '''

        ret_object = copy.deepcopy(self)

        def dfs_push(current):

            if isinstance(current, Negation):

                if current.is_onf():

                    return current

                else:

                    return dfs_push(current.push())

            elif isinstance(current, Predicate):

                return current

            elif isinstance(current, Quantifier):

                return type(current)(current.variables, [dfs_push(x) for x in current.get_term()])

            else:

                return type(current)([dfs_push(x) for x in current.get_term()])

        marked = dfs_push(ret_object)

        return marked

    def is_onf(self):
        '''
        Not in ONF unless we're applied to a Predicate
        '''

        if isinstance(self.term(), Predicate):

            return True

        return False

    def to_onf(self):

        if self.is_onf():

            return copy.deepcopy(self)

        else:

            raise ValueError("Should have already pushed negation prior to ONF")

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "~{}".format(repr(self.term()))
