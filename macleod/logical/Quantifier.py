"""
@author Robert Powell
@version 0.0.2
"""

import macleod.logical.Logical as Logical
import macleod.logical.Symbol as Symbol

import copy

class Quantifier(Logical.Logical):

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
        Really a quantifier is in onf only if it's applied term is in onf
        '''

        return self.terms[0].is_onf()

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

    def simplify(self):
        '''
        Absorb the quantifiers
        '''

        ret_object = copy.deepcopy(self)

        def dfs_simplify(current, parent, root):

            if parent != current:
                # Quantifier: either Absorb or Reset
                if isinstance(current, Quantifier):

                    if parent != None:

                        if isinstance(current, type(root)):
                            # Absorb
                            root.add_variables(current.variables)
                            parent.remove_term(current)
                            parent.set_term(current.get_term())

                        else:
                            # Reset our root
                            root = current

            for term in [x for x in current.get_term() if not isinstance(x, Symbol.Predicate)]:
                dfs_simplify(term, current, root)

        dfs_simplify(ret_object, None, ret_object)
        return ret_object

    def rescope(self):
        '''
        Return a new object that has pulled all quantifiers to the front and
        renamed variables as needed. Must be a B
        '''

        # TODO Based on how this is used, can short-circuit subtrees of different quantifier

        ret_object = copy.deepcopy(self)

        def broaden(symbol, parent, quantifier):

            top_q = quantifier[0]

            if parent is not None:
                if isinstance(symbol, Existential) or isinstance(symbol, Universal):

                    symbol_classname = type(symbol).__name__

                    #First fix parent references!
                    parent.remove_term(symbol)
                    parent.set_term(symbol.get_term())

                    #Second version A -- if quantifiers match
                    if isinstance(symbol, type(top_q)):
                        top_q.add_variables(symbol.variables)

                    #Second version B -- if quantifiers don't match
                    else:
                        everything = top_q.get_term()
                        new_quantifier = globals()[symbol_classname](symbol.variables, everything)

                        #Third set upper quantifier to new quantifier
                        top_q.set_term(new_quantifier)
                        quantifier[0] = new_quantifier


        def bfs_broaden(symbol, left):

            quantifier = [symbol]
            seen = set()

            for item in symbol.get_term():
                left.append((item, None))

            while left != []:

                # Need to broaden children who may share quantifier first
                current_parent = left[0][1]
                stack = [x for x in left if (x[1] == current_parent and not isinstance(x, Symbol.Predicate))]
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
                    if not isinstance(item_left[0], Symbol.Predicate):
                        for term in [x for x in item_left[0].get_term() if not isinstance(x, Symbol.Predicate)] :
                            left.append((term, item_left[0]))

        bfs_broaden(ret_object, [])
        return ret_object

    def rename(self, translation):

        obj = copy.deepcopy(self)

        def dfs_rename(current, translation):

            if isinstance(current, Symbol.Predicate):

                for idx, var in enumerate(current.variables):

                    if var in translation:

                        current.variables[idx] = translation[var]

            else:

                _ = [dfs_rename(x, translation) for x in current.get_term()]

        dfs_rename(obj, translation)
        return obj

    def coalesce(self, other):

        import macleod.logical.Connective as Connective

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
            ret = type(self)(more.variables, Connective.Conjunction(terms))
        else:
            ret = type(self)(more.variables, Connective.Disjunction(terms))

        return ret


class Universal(Quantifier):

    def __init__(self, variables, terms):
        # TODO Allow predicates without names, generate name from class count?

        if isinstance(terms, Logical.Logical):

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

        return "{}({})[{}]".format(u"\u2200", ",".join(self.variables), repr(self.terms[0]))


class Existential(Quantifier):

    def __init__(self, variables, terms):

        if isinstance(terms, Logical.Logical):

            self.terms = [terms]

        elif isinstance(terms, list):

            if len(terms) != 1:
                raise ValueError('Universal must be over a list of Logical')

            self.terms = copy.deepcopy(terms)

        else:

            raise ValueError('Exi must be over a LogicalObject!')

        if not isinstance(variables, list):
            raise ValueError('Predicate variables must be contained in a list!')

        for var in variables:
            if not isinstance(var, str):
                raise ValueError('Predicate variables must be strings!')

        self.variables = copy.deepcopy(variables)

    def __repr__(self):

        return "{}({})[{}]".format(u"\u2203", ",".join(self.variables), repr(self.terms[0]))
