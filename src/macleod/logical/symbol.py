"""
@author Robert Powell
@version 0.0.2
"""

from macleod.logical.logical import Logical

from enum import Enum
import copy
import logging

LOGGER = logging.getLogger(__name__)

def generator():
    '''
    Utility function to ensure that we provide substituted functions
    unique renamed variables.
    '''

    start = 1

    def next_term():

        nonlocal start

        start += 1

        return str(start)

    return next_term

global gen 
gen = generator()

class Predicate(Logical):
    '''
    Representation of a FOL predicate, with convenient mappings for arity and
    variables.
    '''

    DIFFERENT = 0
    SAME = 1
    INVERTED = 2
    OTHER = 3
    CHAIN = 4

    # TODO: need to read translations from file
    SYMBOL_TRANSLATIONS = {'<': 'lt',
                           '>': 'gt',
                           '<=': 'leq',
                           '>=': 'geq'}


    # TODO Implement smart scoping, quantifier resolution for variables?
    def __init__(self, name, variables):

        if not isinstance(name, str):
            raise ValueError('Predicate names must be string!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str) and not isinstance(var, Function):
                raise ValueError('Predicate variables must be strings or Functions!')

        # Do predicate name substitution to eliminate any special symbols (like <, >= not accepted by reasoners)
        self.name = self.SYMBOL_TRANSLATIONS.get(name, name)

        # Make sure you make a COPY of everything, no references!
        self.variables = variables[:]

        self.variable_generator = generator()

    def same_symbol(self, other):
        '''
        Compare against another predicate symbol and report whether they have the same name;
        the arity and variable names are NOT compared

        :param Predicate other, predicate to compare against
        :return Boolean
        '''

        if not isinstance(other, Predicate) and not isinstance(other, Function):

            LOGGER.warning('Should only compare predicates to predicates or function symbols')
            return False

        #if len(other.variables) != len(self.variables):
        #    return False

        if other.name == self.name:
            return True

        return False


    def compare(self, other):
        '''
        Compare against another Predicate and report different, same, inverse, or chained variables;
        the predicate names are NOT compared

        :param Predicate other, predicate to compare against
        '''

        if not isinstance(other, Predicate):
            raise ValueError('Can only compare predicates to predicates')

        if len(other.variables) != len(self.variables):
            return Predicate.DIFFERENT

        if other.variables == self.variables:
            return Predicate.SAME

        if list(reversed(other.variables)) == self.variables:
            return Predicate.INVERTED

        # both are length 2, not inverted but the other's first variable matches this second ones, we have a chain
        if len(self.variables)==2 and len(other.variables)==2 and self.variables[1]==other.variables[0]:
            return Predicate.CHAIN

        return Predicate.OTHER

    def has_functions(self):
        '''
        Return true if contains nested functions
        '''

        for var in self.variables:

            if isinstance(var, Function):
                return True

        return False

    def substitute_function(self, negated = False):
        '''
        Find a function that's nested and replace it by adding a new variable and term
        '''

        # TODO Dirty hack because cyclic imports are painful
        from macleod.logical.quantifier import (Universal, Existential, Quantifier)
        from macleod.logical.negation import Negation
        from macleod.logical.connective import (Conjunction, Disjunction, Connective)

        global gen

        def sub_functions(term, predicates, variables):
            '''
            Does three things: (1) returns a variable that serves as the placeholder 
            for the function. (2) adds a minted predicate to the accumulator (3) adds
            any the newly introduced variable for each function to the accumulator
            '''

            # Singleton used to access an increasing integer sequence
            global gen

            # Base Case 0: I'm not event a function, I'm a variable
            if isinstance(term, str):
                
                # Already existing variables should be quantified don't rescope them
                return term

            # Base Case 1: I'm a function with no nested functions!
            if isinstance(term, Function) and term.has_functions() == False:

                # Mint a new variable special
                new_variable = term.name.lower()[0] + gen()
                variables.append(new_variable)

                # Mint a new predicate with our original variables + the new one
                predicate_variables = term.variables
                predicate_variables.append(new_variable)

                predicate = Predicate(term.name, predicate_variables)
                predicates.append(predicate)

                # Return our fresh variable
                return new_variable

            # Recursive Case: I'm a function with nested functions!
            if isinstance(term, Function): #and term.has_functions() == True:

                # Still mint a new variable cuz I'm still a function
                new_variable = term.name.lower()[0] + gen()
                variables.append(new_variable)

                # Assemble my variables by a DFS down on my function / atom children
                predicate_variables = [sub_functions(x, predicates, variables) for x in term.variables]
                predicate_variables.append(new_variable)

                predicate = Predicate(term.name, predicate_variables)
                predicates.append(predicate)

                return new_variable

        predicate_accumulator = []
        variable_accumulator = []

        variables = [sub_functions(x, predicate_accumulator, variable_accumulator) for x in self.variables]
        if len(predicate_accumulator) > 1:
            term = Conjunction(predicate_accumulator)
        else:
            term = predicate_accumulator[0]

        predicate = Predicate(self.name, variables)

        if negated:
            # The negation cancels out the normal conditional breakdown
            universal = Universal(variable_accumulator, predicate | ~term)
        else:
            universal = Universal(variable_accumulator, predicate | ~term)

        return universal, predicate_accumulator

    def is_equality(self):
        if self.name=='=':
            if len(self.variables)==2:
                return True
            else:
                raise ValueError('Equality predicate must have exactly two variables')
        else:
            return False

    def is_onf(self):
        '''
        In ONF unless we've got a nested function...
        '''

        for var in self.variables:

            if isinstance(var, Function):
                return False

        return True

    def to_onf(self):

        return self

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "{}({})".format(self.name, ",".join([(v if isinstance(v, str) else repr(v)) for v in self.variables]))

    def __eq__(self, other):
        """
        Test if two predicates are equal to each other

        :param Predicate other, the predicate we compare against
        :return Boolean result
        """

        return repr(self) == repr(other)

class Function(Logical):
    '''
    Represents a FOL function, convenience class to quickly enable function substitution
    '''

    def __init__(self, name, variables):

        if not isinstance(name, str):
            raise ValueError('Function names must be string!')

        if not isinstance(variables, list):
            raise ValueError('Function variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str) and not isinstance(var, type(self)):
                raise ValueError('Function variables must be strings or functions!')

        self.name = name
        # Make sure you make a COPY of everything, no references!
        self.variables = variables[:]

    def has_functions(self):
        '''
        Return true if contains nested functions
        '''

        for var in self.variables:

            if isinstance(var, Function):
                return True

        return False

    def same_symbol(self, other):
        '''
        Compare against another Function symbol and report whether they have the same name and arity;
        the variable names therein are NOT compared

        :param Predicate other, predicate to compare against
        :return Boolean
        '''

        if not isinstance(other, Function) and not isinstance(other, Predicate):

            LOGGER.warning('Should only compare function symbols to other function or predicate symbols')
            return False

        if len(other.variables) != len(self.variables):
            return False

        if other.name == self.name:
            return True

        return False


    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "{}({})".format(self.name.lower(), 
                ",".join([v if isinstance(v, str) else repr(v) for v in self.variables]))

