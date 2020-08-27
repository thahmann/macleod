"""
@author Robert Powell
@version 0.0.2

"""

import copy
import functools
import logging

from macleod.logical.logical import Logical
from macleod.logical.quantifier import (Universal, Existential, Quantifier)

LOGGER = logging.getLogger(__name__)

class Connective(Logical):
    '''
    Base class for Conjunctions and Disjunctions. Holds most of the business
    logic.
    '''

    def __init__(self, terms):

        super().__init__()

        if not isinstance(terms, list):
            raise ValueError("{} expects a list of terms".format(type(self)))

        if len(terms) < 2:
            LOGGER.debug(terms)
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

        if not isinstance(t_one, Logical):
            raise ValueError("Can only distribute with Logicals")

        if not isinstance(t_two, Connective):

            # Automatically switch if we have parameters backwards
            if isinstance(t_one, Connective) and isinstance(t_two, Logical):
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

    def coalesce(self):
        '''
        Coalesce or merge any like quantifiers held as terms of this
        connective. Conjunctions will coalesce Universals and will merge
        Existentials.
        '''

        obj = copy.deepcopy(self)

        LOGGER.debug("Coalesced Called: " + repr(obj))
        quantifiers = [x for x in obj.get_term() if isinstance(x, Quantifier)]

        # Short circuit case where we have only one quantifier
        if len(quantifiers) == 1:
            return obj

        coalesce = Universal if isinstance(self, Conjunction) else Existential
        merge = Universal if isinstance(self, Disjunction) else Existential

        to_coalesce = [x for x in obj.terms if isinstance(x, coalesce)]
        to_merge = [x for x in obj.terms if isinstance(x, merge)]

        coalesced = None
        merged = None

        if len(to_coalesce) > 1:

            LOGGER.debug("Coalescing type: " + repr(coalesce))
            coalesced = functools.reduce(lambda x, y: x.coalesce(y), to_coalesce)

        if len(to_merge) > 1:

            LOGGER.debug("Merging type: " + repr(merge))

            variables = []
            terms = []

            for quant in to_merge:

                variables.extend(quant.variables)
                terms.extend(quant.get_term())

            merged_terms = [type(self)(terms)]
            merged = merge(variables, merged_terms)

        other_terms = [x for x in obj.get_term() if (x not in to_coalesce) and (x not in to_merge)]

        if coalesced is not None:

            # Ensure we reduce the resulting connective in the new quantifier
            coalesced.reduce()

        if merged is not None:

            # Ensure we reduce the resulting connective in the new quantifier
            merged.reduce()

        if len(other_terms) == 0:

            if coalesced is not None and merged is None:
                return coalesced

            elif merged is not None and coalesced is None:
                return merged

            elif merged is None and coalesced is None:
                # Basically we're already coalesced with two quantifiers
                return self

            else:
                return type(self)([coalesced, merged])

        else:

            if coalesced is not None:
                LOGGER.debug("Adding Coalesced: " + repr(coalesced))
                other_terms.append(coalesced)

            if merged is not None:
                LOGGER.debug("Adding Merged: " + repr(coalesced))
                other_terms.append(merged)

            if merged is None and coalesced is None:
                # Already coalesced with extra non quantifier terms
                return self
            
            LOGGER.debug(other_terms)
            return type(self)(other_terms)

    def rescope(self, parent=None):
        '''
        Observe the quantifier children and promote one of them. 

        Precondition: Already has had like children coalesced
        '''

        LOGGER.debug("Rescope Called: " + repr(self))
        quantifiers = [x for x in self.get_term() if isinstance(x, Quantifier)]

        if len(quantifiers) == 0:

            LOGGER.debug("No Quantifier children: " + repr(self))
            return copy.deepcopy(self)

        # Handle trivial case of single quantifier
        elif len(quantifiers) == 1:
            LOGGER.debug("Rescoping: Single quantifier")

            # Begin by getting the type of soon to be rescoped quantifier
            quantifier = quantifiers.pop()

            # Get all the terms held by the quantifier
            terms = quantifier.get_term()

            # Add the other terms to from this connective to terms
            terms.extend([x for x in self.get_term() if x != quantifier])

            # Create a new connective using the terms
            connective = type(self)(copy.deepcopy(terms))

            # Call rescope on the connective to rebuild the prenex chain
            rescoped_connective = connective.rescope()

            # Copy the quantifier to a new quantifier with the new connective
            rescoped_quantifier = type(quantifier)(quantifier.variables, rescoped_connective)

            return rescoped_quantifier

        elif len(quantifiers) == 2:

            # Two quantifiers requires that a lookahead be specified
            if parent is None:
                raise ValueError("More than one choice of quantifier, require lookahead value")

            q_type = None
            if isinstance(parent, Conjunction) or isinstance(parent, Universal):
                q_type = Universal

            elif isinstance(parent, Disjunction) or isinstance(parent, Existential):
                q_type = Existential

            # Negation should be pushed in at this point so this should never happen
            if q_type is None:
                raise ValueError("Something Borked itself in a great but terrible way!")

            dominant_quantifier = [x for x in self.get_term() if isinstance(x, q_type) and isinstance(x, Quantifier)]
            weaker_quantifier = [x for x in self.get_term() if not isinstance(x, q_type) and isinstance(x, Quantifier)]

            if len(dominant_quantifier) != 1 or len(weaker_quantifier) != 1:
                raise ValueError("More than a single type of quantifier found, did you coalesce?")

            # Should have only of one of each
            LOGGER.debug('Number of weaker quantifiers: ' + str(len(weaker_quantifier)) + ' are ' + repr(weaker_quantifier[0]))
            LOGGER.debug('Number of dominant quantifiers: ' + str(len(dominant_quantifier)) + ' are ' + repr(dominant_quantifier[0]))

            # Build the new connective
            new_terms = dominant_quantifier[0].get_term()
            new_terms.extend(weaker_quantifier[0].get_term())
            new_terms.extend([x for x in self.get_term() if x != dominant_quantifier[0] and x != weaker_quantifier[0]])
            new_connective = type(self)(new_terms)

            # Create the inner quantifier to serve as a lookahead
            weaker = type(weaker_quantifier[0])(weaker_quantifier[0].variables, new_connective)

            # Need to ensure we leave partial pre-nex in good form after rescoping
            coalesce = new_connective.coalesce()
            print(coalesce)
            if isinstance(coalesce, Quantifier):
                rescoped_connective = coalesce.rescope()
            elif isinstance(coalesce, Connective):
                rescoped_connective = coalesce.rescope(weaker)

            weaker.set_term(rescoped_connective)

            # Finally create our new head of the prenex
            stronger = type(dominant_quantifier[0])(dominant_quantifier[0].variables, weaker)
            LOGGER.debug("Rescoped Prenex: " + repr(stronger))

            return stronger

        else:

            # This only happens when the parsed axioms has a Connective with > 2 axioms at the leaf level
            return self.rescope(self.coalesce())

            LOGGER.error("Shouldn't be rescoping unless we have coalesced!")
            exit(1)


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

            if isinstance(term, Quantifier):

                raise ValueError("Quantifier within connective during ONF")

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

            return copy.deepcopy(self)

        else:

            LOGGER.debug("Conjunction: " + repr(self) + " not in CNF!")
            
            new_terms = []

            for term in copy.deepcopy(self.terms):

                if term.is_onf():

                    new_terms.append(term)

                else:

                    LOGGER.debug("Culprit non-CNF term is: " + repr(term))
                    new_terms.append(term.to_onf())

            ret = Conjunction(new_terms)
            LOGGER.debug("Returning new Conjunction : " + repr(ret))
            return ret



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

            elif isinstance(term, Quantifier):
                raise ValueError("Found nested quantifier in disjunction!")

            elif isinstance(term, Disjunction):
                raise ValueError("Found nested disjunction within disjunction")

        return True

    def to_onf(self):
        '''
        Determine if this disjunction is currently in CNF form. The only way
        this isn't true is if there is a nested conjunction found. In this
        case, distribute another term (randomly chosen...) over the nested
        conjunction.
        '''

        working = copy.deepcopy(self)

        if self.is_onf():

            return copy.deepcopy(self)

        LOGGER.debug("Disjunction: " + repr(self) + " is not in CNF")


        conjunct = None
        terms = working.get_term()

        # Search for the nested conjunction
        for term in terms:
            if isinstance(term, Conjunction):
                LOGGER.debug("Culprit is nested conjunction: " + repr(term))
                conjunct = term
                break

        # Pick a distribute term that isn't our conjunct
        # TODO: Hueristic, always pick the smallest other term first
        distributive_term = terms[0] if terms[0] != conjunct else terms[1] 

        other_terms = [x for x in terms if (x != conjunct and x != distributive_term)]

        distributed = working.distribute(distributive_term, conjunct)

        return distributed.to_onf()
