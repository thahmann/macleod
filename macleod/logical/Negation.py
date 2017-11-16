"""
@author Robert Powell
@version 0.0.2
"""

import macleod.logical.Logical as Logical
import macleod.logical.Connective as Connective
import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier

import copy

class Negation(Logical.Logical):
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

        elif isinstance(terms, Logical.Logical):

            self.terms = [copy.deepcopy(terms)]

        else:

            raise ValueError("Negation not init'd right")

    def set_term(self, terms):

        if isinstance(terms, list):
            if len(terms) != 1:
                raise ValueError("Must apply negation to a single element")

            term = copy.deepcopy(terms.pop())
            self.terms = [term]

        elif isinstance(terms, Logical.Logical):

            self.terms = [copy.deepcopy(terms)]

        else:

            raise ValueError("Negation must be passed a list or Logical")

    def term(self):

        return copy.deepcopy(self.terms[0])

    def push(self):
        '''
        Push negation inwards and apply to all children
        '''

        # Can be a conjunction or disjunction
        # Can be a single predicate
        # Can be a quantifier

        if isinstance(self.term(), Connective.Conjunction):

            ret = Connective.Disjunction([Negation(x) for x in self.term().get_term()])

        elif isinstance(self.term(), Connective.Disjunction):

            ret = Connective.Conjunction([Negation(x) for x in self.term().get_term()])

        elif isinstance(self.term(), Symbol.Predicate):

            ret = self

        elif isinstance(self.term(), Quantifier.Existential):

            ret = Quantifier.Universal(self.term().variables, Negation(self.term().get_term()))

        elif isinstance(self.term(), Quantifier.Universal):

            ret = Quantifier.Existential(self.term().variables, Negation(self.term().get_term()))

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

            elif isinstance(current, Symbol.Predicate):

                return current

            elif isinstance(current, Quantifier.Quantifier):

                return type(current)(current.variables, [dfs_push(x) for x in current.get_term()])

            else:

                return type(current)([dfs_push(x) for x in current.get_term()])

        marked = dfs_push(ret_object)

        return marked

    def is_onf(self):
        '''
        Not in ONF unless we're applied to a Predicate
        '''

        if isinstance(self.term(), Symbol.Predicate):

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
