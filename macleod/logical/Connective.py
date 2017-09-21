"""
@author Robert Powell
@version 0.0.2

"""

import copy
import functools

import macleod.logical.Logical as Logical
import macleod.logical.Quantifier as Quantifier

class Connective(Logical.Logical):
    '''
    Base class for Conjunctions and Disjunctions. Holds most of the business
    logic.
    '''

    def __init__(self, terms):

        super().__init__()

        if not isinstance(terms, list):
            raise ValueError("{} expects a list of terms".format(type(self)))

        if len(terms) < 2:
            raise ValueError("{} requires at least two terms".format(type(self)))

        for term in terms:

            # Absorb like-connectives on initialization
            if isinstance(term, type(self)):
                self.terms.extend(copy.deepcopy(term.get_term()))

            else:
                self.terms.append(copy.deepcopy(term))

    def remove_term(self, term):

        return self.terms.remove(term)

    def set_term(self, term):

        if isinstance(term, type(self)):
            self.terms.extend(copy.deepcopy(term.get_term()))

        elif isinstance(term, list):
            self.terms.extend(copy.deepcopy(term))
        else:
            self.terms.append(copy.deepcopy(term))


    def distribute(self, t_one, t_two):
        '''
        Provides a self-mutating ability to distribute two terms contained in
        this connective. Uses some neat reflection to handle both cases within
        this single base class.

        :param Connective self, Object that distribute is being called on
        :param Logical t_one, Logical we are distributing with
        :param Connective t_two, Connective we are distributing over
        :return None
        '''

        save_term = copy.deepcopy(self.terms)

        if not isinstance(t_one, Logical.Logical):
            raise ValueError("Can only distribute with Logicals")

        if not isinstance(t_two, Connective):

            # Automatically switch if we have parameters backwards
            if isinstance(t_one, Connective) and isinstance(t_two, Logical.Logical):
                return self.distribute(t_two, t_one)
            else:
                raise ValueError("Can only distribute over Connectives!")

        if t_one == t_two:
            raise ValueError("Can't distribute terms over themselves")

        if (t_one not in self.terms) or (t_two not in self.terms):
            raise ValueError("Can't distribute terms that aren't members")

        # Not really distribution, just absorption
        if isinstance(t_two, type(self)):

            self.remove_term(t_two)
            self.set_term(copy.deepcopy(t_two.get_term()))

        # The real distribution
        else:

            self.remove_term(t_one)
            self.remove_term(t_two)

            local = type(self)
            other = type(t_two)

            other_terms = copy.deepcopy(t_two.get_term())
            new_term = other([local([copy.deepcopy(t_one), t]) for t in other_terms])

            self.set_term(new_term)

        # Save off edited self
        altered_self = copy.deepcopy(self)
        self.terms = save_term

        # If we only contain the new element return it
        if len(altered_self.get_term()) == 1:
            return new_term

        else:
            return altered_self

    def rescope(self, parent=None):
        '''
        Look at children quantifiers along with parent to decide which
        quantifier to pull out to the front.

        Precondition: Already has had like children coalesced
        
        '''

        # Need to update this a few ways
        # 1.) Return a new connective
        # 2.) Don't screw around with parent classes
        # 3.) Handle the case where we promote the only available quantifier


        # Handle trivial case of single quantifier
        quantifiers = [x for x in self.get_term() if isinstance(x, Quantifier.Quantifier)]
        if len(quantifiers) == 1:

            quant = quantifiers.pop()
            new_terms = quant.get_term()
            new_terms.extend([x for x in self.get_term() if x != quant])
            new_connective = type(self)(new_terms)

            return type(quant)(quant.variables, new_connective)

        # Handle lookahead case where two choices exist
        if parent is None:
            raise ValueError("More than one choice of quantifier, require lookahead value")

        quantifier_type = None
        if isinstance(parent, Conjunction):
            q_type = Quantifier.Universal

        elif isinstance(parent, Disjunction):
            q_type = Quantifier.Existential

        if q_type is None:
            raise ValueError("WHATTTTTTT")

        dominant_quantifier = [x for x in self.get_term() if isinstance(x, q_type)]
        weaker_quantifier = [x for x in self.get_term() if not isinstance(x, q_type)]

        if (len(weaker_quantifier) + len(dominant_quantifier)) != 2:
            raise ValueError("Need to coalesce quantifiers before rescoping!")

        # Build the new connective
        new_terms = dominant_quantifier[0].get_term()
        new_terms.extend(weaker_quantifier[0].get_term())
        new_terms.extend([x for x in self.get_term() if x != dominant_quantifier[0] and x != weaker_quantifier[0]])
        new_connective = type(self)(new_terms)
        weaker = type(weaker_quantifier[0])(weaker_quantifier[0].variables, new_connective)
        stronger = type(dominant_quantifier[0])(dominant_quantifier[0].variables, weaker)

        return stronger


class Conjunction(Connective):
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

        super().__init__(terms)

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "({})".format(" & ".join([repr(t) for t in self.terms]))

    def is_onf(self):
        '''
        A conjunction really is always in onf form, these calls only apply to
        the top level. Elements aren't counted.
        '''

        for term in self.get_term():

            if isinstance(term, Quantifier.Quantifier):
                return False

        return True

    def to_onf(self):
        '''
        So long as there are no nested quantifiers it should always be clear
        '''

        if self.is_onf():
            return copy.deepcopy(self)
        else:
            raise ValueError("Broaden quantifiers first skippy!")

    def coalesce(self):
        '''
        Look through for any quantifier children that should be merged
        '''

        obj = copy.deepcopy(self)

        universals = [x for x in obj.terms if isinstance(x, Quantifier.Universal)]

        if len(universals) == 0:
            return self

        new_universal = functools.reduce(lambda x, y: x.coalesce(y), universals)

        if len(universals) == len(obj.terms):

            return new_universal

        else:

            for term in universals:
                obj.remove_term(term)

            obj.set_term(new_universal)
            return obj


class Disjunction(Connective):
    '''
    Representation of a FOL disjunction. Provides nice mappings for
    distribution, terms, and other logical operations.
    '''

    def __init__(self, terms):
        '''
        Expect that a conjunction is constructed with at least two terms.

        :param list terms, List of LogicalObjects
        :return Disjunction
        '''

        super().__init__(terms)

    def __repr__(self):
        '''
        Allow nice printing of Conjunctions

        :return self.__repr__() method
        '''

        return "({})".format(" | ".join([repr(t) for t in self.terms]))

    def is_onf(self):
        '''
        If we have a nested conjunction we have a problem.
        '''

        for term in self.get_term():

            if isinstance(term, Conjunction):
                return False

            elif isinstance(term, Quantifier.Quantifier):
                return False

        return True

    def to_onf(self):
        '''
        Precondition: It doesn't have any quantifiers as children:w
        Postcondition: Without recursion this term is happy being a 
        '''

        is_onf = False
        ret = copy.deepcopy(self)

        if self.is_onf():
            return copy.deepcopy(self)

        while not is_onf:

            over = None
            terms = ret.get_term()

            for term in terms:

                if isinstance(term, Conjunction):

                    over = term
                    break

                elif isinstance(term, Quantifier.Quantifier):

                    raise ValueError('Broaden quantifiers first skippy!')

            # Hueristic to distribute smarter?
            distribute = terms[0] if terms[0] != over else terms[1] 

            ret = ret.distribute(distribute, over)

            if ret.is_onf():
                is_onf = True

        return ret

    def coalesce(self):
        '''
        Look through for any quantifier children that should be merged
        '''

        obj = copy.deepcopy(self)

        existentials = [x for x in obj.terms if isinstance(x, Quantifier.Existential)]

        if len(existentials) == 0:

            return self

        new_existential = functools.reduce(lambda x, y: x.coalesce(y), existentials)

        if len(existentials) == len(obj.terms):

            return new_existential

        else:

            for term in existentials:
                obj.remove_term(term)

            obj.set_term(new_existential)
            return obj
