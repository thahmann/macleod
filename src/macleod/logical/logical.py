"""
@author Robert Powell
@version 0.0.2

Base class representing what is the object structure of Macleod. General idea
is that the majority of the Logical operations should return new copies of
stuff, alas that doesn't always work so you'll notice some state mutations.
These mutating functions are meant to be called from some other utility
structure that will appropriately copy as needed to keep the original structure
normal
"""


class Logical(object):
    '''
    Represents the base class that all terms will have in common.
    '''

    def __init__(self):

        # Serves as the dynamic storage location for nesting within the object
        # structure. Each Logical type has various restrictions on what can or
        # cannot be placed within this storage. It is the responsibility of the
        # child classes to maintain consistency with their definitions.
        self.terms = []

    def __and__(self, other):
        '''
        Operator overload for the '&' command, to simplify first-order logic
        operations.

        :return Conjunction()
        '''

        from macleod.logical.connective import (Conjunction, Disjunction, Connective)

        return Conjunction([self, other])

    def __or__(self, other):
        '''
        Operator overload for the '|' command, to simplify first-order logic
        operations.

        :return Disjunction()
        '''

        from macleod.logical.connective import (Conjunction, Disjunction, Connective)

        return Disjunction([self, other])

    def __invert__(self):
        '''
        Operator overload for the '~' command, to simplify first-order logic
        operations.

        :return Negation()
        '''

        from macleod.logical.negation import Negation

        return Negation(self)

    def remove_term(self, term):
        '''
        Function stub for removal accessor
        '''

        raise NotImplementedError

    def set_term(self, term):
        '''
        Function stub for setter accessor
        '''

        raise NotImplementedError

    def get_term(self):
        '''
        Function stub for getter accessor
        '''

        return self.terms
    
    def is_onf(self):
        '''
        Method that determines, from the view of this Logical, if it is in
        Object Normal Form. Object normal form is just another name for CNF
        minus any of the skolemization or functions. Does not recurse into
        children to test for ONF!

        :precondition FF and no nested Quantifiers
        :return Boolean, True or False depending on ONF state
        '''

        raise NotImplementedError

    def to_onf(self):
        '''
        Method that translate, from the view of this Logical, to Object Normal
        Form. Object normal form is just another name for CNF minus any of the
        skolemization or functions. Does not recurse into children to test for
        ONF!

        :precondition FF and no nested Quantifiers 
        :return Logical, A copy of the logical in ONF form
        '''

        raise NotImplementedError
