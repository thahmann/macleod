"""
@author Robert Powell
@version 0.0.2
"""

import macleod.logical.Logical as Logical

import copy

class Predicate(Logical.Logical):
    '''
    Representation of a FOL predicate, with convenient mappings for arity and
    variables.
    '''

    # TODO Implement smart scoping, quantifier resolution for variables?
    def __init__(self, name, variables):

        if not isinstance(name, str):
            raise ValueError('Predicate names must be string!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str) and not isinstance(var, Function):
                raise ValueError('Predicate variables must be strings or Functions!')

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

    def substitute_function(self):
        '''
        Find a function that's nested and replace it by adding a new variable and term
        '''

        # TODO This a dirty hack because cyclic imports are painful
        import macleod.logical.Quantifier as Quantifier

        if not self.has_functions():
            return self
        
        for idx, var in enumerate(self.variables):

            if isinstance(var, Function):

                function = var
                pos = idx

        # TODO Get a global variable singleton
        n_var = function.name.lower()[0] + '1'
        f_vars = copy.deepcopy(function.variables)
        f_vars.append(n_var)
        n_pred = Predicate(function.name, f_vars)
        e_vars = copy.deepcopy(self.variables)
        e_vars[pos] = n_var
        e_pred = Predicate(self.name, e_vars)

        return Quantifier.Universal([n_var], [e_pred & n_pred]), None


    def is_onf(self):
        '''
        In ONF unless we've got a nested function...
        '''

        for var in self.variables:

            if isinstance(var, Function):
                return False

        return True

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "{}({})".format(self.name, ",".join([(v if isinstance(v, str) else repr(v)) for v in self.variables]))

class Function(Logical.Logical):
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

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "{}({})".format(self.name.lower(), 
                ",".join([v if isinstance(v, str) else repr(v) for v in self.variables]))




