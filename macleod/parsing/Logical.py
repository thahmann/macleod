"""
@author Robert Powell
@version 0.0.1

Collection of classes that are used to represent the first-order logic
sentences specified in common logic interchange format. These exist in order to
simplify management and record-keeping when working with these sentences,
performing translations, etc. ALL OPERATIONS SHALL BE NONE MUTATING. Dealing
with side-effects is painful in these nested structures and to maintain
consistency any LogicalObject should be considered static after its
initialization. There is no construct in Python to enforce this behaivor so
it's up to the developer to make sure they only work with the objects through
the interface.
"""

import copy
import functools


class LogicalObject(object):
    '''
    Represents the base class that all terms will have in common.
    '''

    def __mul__(self, other):
        '''
        Operator overload for the '*' command, to simplify first-order logic
        operations.

        :return NotImplemented
        '''

        return NotImplemented

    def __and__(self, other):
        '''
        Operator overload for the '&' command, to simplify first-order logic
        operations.

        :return NotImplemeneted
        '''

        # TODO Yes, the parent class is instantiating its children...
        return Conjunction([copy.deepcopy(self), copy.deepcopy(other)])

    def __or__(self, other):
        '''
        Operator overload for the '|' command, to simplify first-order logic
        operations.

        :return NotImplemeneted
        '''

        # TODO Yes, the parent class is instantiating its children...
        return Disjunction([copy.deepcopy(self), copy.deepcopy(other)])

    def __neg__(self):
        '''
        Operator overload for the '-' command, to simplify first-order logic
        operations.

        :return NotImplemented
        '''

        return Negation(copy.deepcopy(self))

    def __invert__(self):
        '''
        Operator overload for the '~' command, to simplify first-order logic
        operations. Duplicates the effect of the defined '-' operator.

        :return self.__neg__() method
        '''

        return self.__neg__()
    
    def is_cnf(self):
        '''
        Some scary Python mojo going on here!
        '''

        if isinstance(self, Predicate):

            return True

        elif isinstance(self, Negation):

            if isinstance(self.term, Predicate):
                return True
            else:
                return False

        elif isinstance(self, Disjunction):

            for term in self.terms:
                if isinstance(term, Conjunction):
                    return False

            return all([x.is_cnf() for x in self.terms])

        elif isinstance(self, Conjunction):

            return all([x.is_cnf() for x in self.terms])

        elif isinstance(self, Existential):

            return self.term.is_cnf()

        elif isinstance(self, Universal):

            return self.term.is_cnf()

        else:

            return True

    def remove_term(self, term):

        if isinstance(self, LogicalConnective):

            print("DIDNT HAPPEN?")
            self.terms.remove(term)

        elif isinstance(self, Predicate):
            return []

        else:
            self.term.remove(term)

    def set_term(self, term):

        if isinstance(self, LogicalConnective):

            self.terms.append(copy.deepcopy(term))

        elif isinstance(self, Predicate):

            return []

        else:

            self.term = copy.deepcopy(term)

    def get_term(self):

        if isinstance(self, LogicalConnective):

            return self.terms

        elif isinstance(self, Predicate):
            return []

        else:

            return [self.term]


class LogicalQuantifier(LogicalObject):

    def __init__(self):

        self.variables = []
        self.term = None

    def dfs_traverse(self, function):


    def rescope(self):
        '''
        Return a new object that has pulled all quantifiers to the front and
        renamed variables as needed. Must be a B
        '''

        ret_object = copy.deepcopy(self)

        def broaden(symbol, parent, quantifier):

            top_q = quantifier[0]

            print(symbol, parent, quantifier)


            if parent is not None:
                # We've 
                if isinstance(symbol, Existential) or isinstance(symbol, Universal):

                    symbol_classname = type(symbol).__name__

                    #First fix parent references!
                    parent.remove_term(symbol)
                    parent.set_term(symbol.term)

                    #Second version A -- if quantifiers match
                    if isinstance(symbol, type(top_q)):
                        print("SHOULD HAVE REMOVED MYSELF")
                        top_q.variables += symbol.variables

                    #Second version B -- if quantifiers don't match
                    else:
                        everything = top_q.term
                        new_quantifier = globals()[symbol_classname](symbol.variables, everything)

                        #Third set upper quantifier to new quantifier
                        top_q.set_term(new_quantifier)
                        quantifier[0] = new_quantifier


        def traverse(symbol, left):

            #NOTE Assumes that the sentence is quantifier and the root is a quantifier
            #NOTE Also assumes that cycle aren't a problem for now
            quantifier = [symbol]
            seen = set()

            for item in symbol.get_term():
                left.append((item, None))

            while left != []:

                # Need to broaden children who may share quantifier first
                current_parent = left[0][1]
                stack = [x for x in left if x[1] == current_parent]
                for item in stack:
                    print(quantifier)
                    if isinstance(item[0], type(quantifier[0])):
                        broaden(item[0], item[1], quantifier)
                        left.remove(item)
                        for term in item[0].get_term():
                            left.append((term, item[0]))
                        stack.remove(item)

                for item_left in stack:
                    broaden(item_left[0], item_left[1], quantifier)
                    left.remove(item_left)
                    for term in item_left[0].get_term():
                        left.append((term, item_left[0]))

                #current, parent = left.pop(0)
                #broaden(current, parent, quantifier) 

                #for term in current.get_term():
                #    left.append((term, current))

        traverse(ret_object, [])
        return ret_object

                

class LogicalConnective(LogicalObject):

    def __init__(self):

        self.terms = []

class Universal(LogicalQuantifier):

    def __init__(self, variables, term):
        # TODO Allow predicates without names, generate name from class count?

        if not isinstance(term, LogicalObject):
            raise ValueError('Universal must be over a LogicalObject!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.variables = copy.deepcopy(variables)
        self.term = copy.deepcopy(term)

    def __repr__(self):

        return "{}({})[{}]".format(u"\u2200", ",".join(self.variables), repr(self.term))


class Existential(LogicalQuantifier):

    def __init__(self, variables, term):
        # TODO Allow predicates without names, generate name from class count?

        if not isinstance(term, LogicalObject):
            raise ValueError('Universal must be over a LogicalObject!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.variables = copy.deepcopy(variables)
        self.term = copy.deepcopy(term)

    def __repr__(self):

        return "{}({})[{}]".format(u"\u2203", ",".join(self.variables), repr(self.term))



class Conjunction(LogicalConnective):
    '''
    Representation of a FOL conjunction. Provides nice mappings for
    distribution, terms, and other logical operations.
    '''

    def __init__(self, terms):
        '''
        Expect that a conjunction is constructed with at least two terms.

        :param list terms, List of LogicalObjects
        :return Conjunction
        '''

        if not isinstance(terms, list):
            raise ValueError("Conjunction expects a list of terms")

        if len(terms) < 2:
            raise ValueError("Conjunction requires at least two terms")

        self.terms = []

        for t in terms:
            if isinstance(t, Conjunction):
                self.terms += copy.deepcopy(t.terms)
            else:
                self.terms.append(copy.deepcopy(t))

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "({})".format(" & ".join([repr(t) for t in self.terms]))

    def distribute(self, term_one, term_two):
        '''
        Overload the of '*' operation signifying distribution. Follows basic
        first-order logic for the distributive property.

        :param LogicalObject self, this disjunction 
        :param LogicalObject term_one, object we are distributing with 
        :param LogicalObject term_two, object we are distributing over
        :return LogicalObject result
        '''

        # TODO Add term de-duplication at some point
        if term_one == term_two:
            raise ValueError("Can't distribute terms over itself")

        if not isinstance(term_one, LogicalObject):
            raise ValueError("Can only distribute over other LogicalObjects")

        if not isinstance(term_two, LogicalObject):
            raise ValueError("Can only distribute over other LogicalObjects")

        if isinstance(term_two, Conjunction):

            # It only makes sense to distribute over internal elements
            self.terms.remove(term_one)
            self.terms.remove(term_two)

            return term_one & term_two

        elif isinstance(term_two, Disjunction):

            # It only makes sense to distribute over internal elements
            self.terms.remove(term_one)
            self.terms.remove(term_two)

            # TODO Heuristic for smarter distribution
            distributive_term = copy.deepcopy(term_one)

            disjunct = Disjunction([distributive_term & term for term in term_two.terms])

            # Did the original conjunction have more than a single term
            if len(self.terms) == 0:
                return disjunct 
            else:
                return disjunct & Conjunction(self.terms)

        elif isinstance(term_two, Predicate):

            if not isinstance(term_one, Predicate):
                return self.distribute(term_two, term_one)
            else:
                raise ValueError("Can't distribute two predicates")


class Disjunction(LogicalConnective):
    '''
    Representation of a FOL disjunction. Provides nice mappings for
    distribution, terms, and other logical operations.
    '''

    def __init__(self, terms):
        '''
        Expect that a disjunction is constructed with at least two terms.

        :param list terms, List of LogicalObjects
        :return Conjunction
        '''

        if not isinstance(terms, list):
            raise ValueError("Conjunction expects a list of terms")

        if len(terms) < 2:
            raise ValueError("Conjunction requires at least two terms")

        self.terms = []

        for t in terms:
            if isinstance(t, Disjunction):
                self.terms += copy.deepcopy(t.terms)
            else:
                self.terms.append(copy.deepcopy(t))

    def distribute(self, term_one, term_two):
        '''
        Overload the of '*' operation signifying distribution. Follows basic
        first-order logic for the distributive property.

        :param LogicalObject self, this disjunction 
        :param LogicalObject term_one, object we are distributing with 
        :param LogicalObject term_two, object we are distributing over
        :return LogicalObject result
        '''

        # TODO Add term de-duplication at some point
        if term_one == term_two:
            raise ValueError("Can't distribute terms over itself")

        if not isinstance(term_one, LogicalObject):
            raise ValueError("Can only distribute over other LogicalObjects")

        if not isinstance(term_two, LogicalObject):
            raise ValueError("Can only distribute over other LogicalObjects")

        if isinstance(term_two, Conjunction):

            # It only makes sense to distribute over internal elements
            self.terms.remove(term_one)
            self.terms.remove(term_two)

            distributive_term = copy.deepcopy(term_one)

            conjunct = Conjunction([distributive_term | term for term in term_two.terms])

            # Did the original conjunction have more than a single term
            if len(self.terms) == 0:
                return conjunct
            else:
                return conjunct | Disjunction(self.terms)

        elif isinstance(term_two, Disjunction):

            # It only makes sense to distribute over internal elements
            self.terms.remove(term_one)
            self.terms.remove(term_two)

            return term_one | term_two

        elif isinstance(term_two, Predicate):

            if not isinstance(term_one, Predicate):
                return self.distribute(term_two, term_one)
            else:
                raise ValueError("Can't distribute two predicates")

        else:
            raise ValueError("Distribution of Conjunction and {} not implemented".format(type(term_two)))

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "({})".format(" | ".join([repr(t) for t in self.terms]))


class Negation(LogicalConnective):
    '''
    Representation of a negation to wrap Predicates, Disjunctions, and
    Conjunctions and Quantifiers.
    '''

    def __init__(self, term):

        if not isinstance(term, LogicalObject):
            raise ValueError("Must pass negation a LogicalObject")


        self.term = copy.deepcopy(term)

    def push(self):
        '''
        Push negation inwards and apply to all children
        '''

        # Can be a conjunction or disjunction
        # Can be a single predicate
        # Can be a quantifier

        if isinstance(self.term, Conjunction):

            ret = Disjunction([Negation(x) for x in self.term.terms])

        elif isinstance(self.term, Disjunction):

            ret = Conjunction([Negation(x) for x in self.term.terms])

        elif isinstance(self.term, Predicate):

            ret = self

        elif isinstance(self.term, Existential):

            ret = Universal(self.term.variables, Negation(self.term.term))

        elif isinstance(self.term, Universal):

            ret = Existential(self.term.variables, Negation(self.term.term))

        else:
            
            raise ValueError("Negation onto unknown type!", self.term)

        return ret

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "~{}".format(repr(self.term))


class Predicate(LogicalObject):
    '''
    Representation of a FOL predicate, with convenient mappings for arity and
    variables.
    '''
    # TODO Implement smart scoping, quantifier resolution for variables?

    def __init__(self, name, variables):
        # TODO Allow predicates without names, generate name from class count?

        if not isinstance(name, str):
            raise ValueError('Predicate names must be string!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.name = name
        # Make sure you make a COPY of everything, no references!
        self.variables = variables[:]

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "{}({})".format(self.name, ",".join([v for v in self.variables]))
