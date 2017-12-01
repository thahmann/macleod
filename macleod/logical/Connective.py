"""
@author Robert Powell
@version 0.0.2

"""

import copy
import functools
import logging

import macleod.logical.Logical as Logical
import macleod.logical.Quantifier as Quantifier

LOGGER = logging.getLogger(__name__)

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

        LOGGER.debug(repr(t_one) + ' -- ' + repr(t_two))

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
        # 4.) Just return if we don't even have a connective
        # 5.) Handle the dirty case where we have a mix of uncoalesable quantifiers


        # Handle trivial case of single quantifier
        quantifiers = [x for x in self.get_term() if isinstance(x, Quantifier.Quantifier)]
        if len(quantifiers) == 0:
            LOGGER.debug("Found no quantifiers")

            # Save off edited self
            return self

        if len(quantifiers) == 1:
            LOGGER.debug("Found one quantifiers")

            quant = quantifiers.pop()
            new_terms = quant.get_term()
            new_terms.extend([x for x in self.get_term() if x != quant])
            new_connective = type(self)(new_terms)

            return type(quant)(quant.variables, new_connective)

        # Handle lookahead case where two choices exist
        if parent is None:
            raise ValueError("More than one choice of quantifier, require lookahead value")

        q_type = None
        if isinstance(parent, Conjunction) or isinstance(parent, Quantifier.Universal):
            q_type = Quantifier.Universal

        elif isinstance(parent, Disjunction) or isinstance(parent, Quantifier.Existential):
            q_type = Quantifier.Existential

        if q_type is None:
            raise ValueError("Something Borked itself in a great but terrible way!")

        dominant_quantifier = [x for x in self.get_term() if isinstance(x, q_type) and isinstance(x, Quantifier.Quantifier)]
        weaker_quantifier = [x for x in self.get_term() if not isinstance(x, q_type) and isinstance(x, Quantifier.Quantifier)]

        LOGGER.debug('Number of weaker quantifiers: ' + str(len(weaker_quantifier)) + ' are ' + str(type(weaker_quantifier[0])))
        LOGGER.debug('Number of dominant quantifiers: ' + str(len(dominant_quantifier)) + ' are ' + str(type(dominant_quantifier[0])))

        if (len(weaker_quantifier) + len(dominant_quantifier)) != 2:
            LOGGER.warning('Next step is experimental!')
            #raise ValueError("Need to coalesce quantifiers before rescoping!")

        # Build the new connective
        new_terms = dominant_quantifier[0].get_term()
        new_terms.extend(weaker_quantifier[0].get_term())
        new_terms.extend([x for x in self.get_term() if x != dominant_quantifier[0] and x != weaker_quantifier[0]])
        new_connective = type(self)(new_terms)
        weaker = type(weaker_quantifier[0])(weaker_quantifier[0].variables, new_connective)
        stronger = type(dominant_quantifier[0])(dominant_quantifier[0].variables, weaker)
        LOGGER.debug("Returning new dominant quantifier: " + repr(stronger))

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
        A Conjunction is in ONF form unless it has children that are
        Conjunctions, or it has any Quantifiers as children.

        :return Conjunction, New ONF conjunction
        '''

        for term in self.get_term():

            if isinstance(term, Quantifier.Quantifier):

                raise ValueError("Quantifer within connective during ONF")

            elif isinstance(term, Conjunction):

                raise ValueError("Has a conjunction nested in a conjunction")

            elif term.is_onf() == False:

                return False

        return True

    def to_onf(self):
        '''
        If this conjunction is not found to be in ONF, call to_onf on that
        child.
        '''

        if self.is_onf():

            LOGGER.debug("Connective in ONF form: " + repr(self))

            return copy.deepcopy(self)

        else:
            
            new_terms = []

            for term in self.terms:

                if term.is_onf():
                    new_terms.append(term)
                else:
                    new_terms.append(term.to_onf())

            return Conjunction(new_terms)

    def coalesce(self):
        '''
        Coalesce or merge any like quantifiers held as terms of this
        connective. Conjunctions will coalesce universals and will merge
        existentials.

        precondition: Must not have both universals and existentials
        '''

        obj = copy.deepcopy(self)

        LOGGER.debug("Attempting to coalesce: " + repr(obj))

        universals = [x for x in obj.terms if isinstance(x, Quantifier.Universal)]
        existentials = [x for x in obj.terms if isinstance(x, Quantifier.Existential)]

        if len(universals) != 0:

            LOGGER.debug("Coalescing Universals")
            new_universal = functools.reduce(lambda x, y: x.coalesce(y), universals)
            LOGGER.debug("Coalesced Universal: " + repr(new_universal))

            if len(universals) == len(obj.terms):

                LOGGER.debug("Returning plain: " + repr(new_universal))

                return new_universal

            else:

                for term in universals:
                    obj.remove_term(term)

                obj.set_term(new_universal)

                LOGGER.debug("Returning added: " + repr(obj))
                return obj

        elif len(existentials) != 0 and len(universals) == 0:

            LOGGER.debug("Merging nested existentials")
            
            variables = []
            terms = []
            for quant in existentials:
                variables += quant.variables
                terms.append(quant.terms[0])

            for term in obj.terms:
                if term not in existentials:
                    terms.append(term)

            
            terms = [type(self)(terms)]
            return Quantifier.Existential(variables, terms)

        else:

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
                raise ValueError("Found nested quantifier in disjunction!")

            elif isinstance(term, Disjunction):
                raise ValueError("Found nested disjunction within disjunction")

        return True

    def to_onf(self):
        '''
        If we have a conjunction nested under the disjunction we need to
        distribute.
        '''

        working = copy.deepcopy(self)

        if self.is_onf():
            return copy.deepcopy(self)

        while True:

            over = None
            terms = working.get_term()

            for term in terms:

                LOGGER.debug("++" + repr(term))
                LOGGER.debug(type(term))

                if isinstance(term, Disjunction):
                    over = term
                    LOGGER.debug("Distributing over a nested Disjunction: " + repr(over))
                    LOGGER.debug("Distributing over a nested Disjunction: " + repr(working))
                    #raise ValueError("Somehow have a disjunction nested in a disjunction")
                    break

                elif isinstance(term, Conjunction):
                    over = term
                    LOGGER.debug("Distributing over a nested Conjunction: " + repr(over))
                    break

                elif isinstance(term, Quantifier.Quantifier):

                    raise ValueError('Broaden quantifiers first skippy!')

                else:

                    LOGGER.debug("Found a Predicate")

            distribute = terms[0] if terms[0] != over else terms[1] 

            if over is not None:
                working = working.distribute(distribute, over)

            LOGGER.debug("Current working: " + repr(working))
            if working.is_onf():
                break

        return working

    def coalesce(self):
        '''
        Coalesce or merge any like quantifiers held as terms of this
        connective. Disjunctions will coalesce existentials and will merge
        universals.
        '''

        obj = copy.deepcopy(self)

        existentials = [x for x in obj.terms if isinstance(x, Quantifier.Existential)]
        universals = [x for x in obj.terms if isinstance(x, Quantifier.Universal)]

        if len(existentials) != 0:

            LOGGER.debug("Coalescing existentials")
            new_existential = functools.reduce(lambda x, y: x.coalesce(y), existentials)

            if len(existentials) == len(obj.terms):
                return new_existential

            else:
                for term in existentials:
                    obj.remove_term(term)

                obj.set_term(new_existential)
                return obj

        elif len(universals) != 0 and len(existentials) == 0:

            LOGGER.debug("Merging nested Universals")
            variables = []
            terms = []
            for quant in universals:
                variables += quant.variables
                terms.append(quant.terms[0])

            for term in obj.terms:
                LOGGER.debug("Adding term: " + repr(term))
                if term not in universals:
                    terms.append(term)

            terms = [type(self)(terms)]
            return Quantifier.Universal(variables, terms)

        else:

            return obj

