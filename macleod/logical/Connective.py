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
        # 5.) Recursively call rescope to ensure that prenexes stay in good form

        quantifiers = [x for x in self.get_term() if isinstance(x, Quantifier.Quantifier)]
        LOGGER.debug("Working TERM: " + repr(self))

        if len(quantifiers) == 0:

            LOGGER.debug("No Quantifier children: " + repr(self))
            return copy.deepcopy(self)

        # Handle trivial case of single quantifier
        if len(quantifiers) == 1:

            # Begin by getting the type of soon to be rescoped quantifier
            quantifier = quantifiers.pop()

            # Get all the terms held by the quantifier
            terms = quantifier.get_term()
            LOGGER.debug("TERMS: " + repr(terms))

            # Add the other terms to from this connective to terms
            terms.extend([x for x in self.get_term() if x != quantifier])
            LOGGER.debug("EXTENDED TERMS: " + repr(terms))

            # Create a new connective using the terms
            connective = type(self)(copy.deepcopy(terms))

            # Call rescope on the connective to rebuild the prenex chain
            LOGGER.debug("Original: " + repr(self))
            LOGGER.debug("++ : " + repr(connective))
            rescoped_connective = connective.rescope()

            LOGGER.debug("MADE IT OUT")
            # Copy the quantifier to a new quantifier with the new connective
            rescoped_quantifier = type(quantifier)(quantifier.variables, rescoped_connective)

            return rescoped_quantifier

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

        if len(dominant_quantifier) != 1 or len(weaker_quantifier) != 1:
            raise ValueError("Should only be choosing to promote between two quantifiers")

        # Should have only of one of each
        LOGGER.debug('Number of weaker quantifiers: ' + str(len(weaker_quantifier)) + ' are ' + repr(weaker_quantifier[0]))
        LOGGER.debug('Number of dominant quantifiers: ' + str(len(dominant_quantifier)) + ' are ' + repr(dominant_quantifier[0]))

        # Build the new connective
        new_terms = dominant_quantifier[0].get_term()
        new_terms.extend(weaker_quantifier[0].get_term())
        new_terms.extend([x for x in self.get_term() if x != dominant_quantifier[0] and x != weaker_quantifier[0]])
        new_connective = type(self)(new_terms)

        # Test: Ensure we maintain the connective chain
        while True:
            new_term = new_connective.coalesce()
            if repr(new_term) == repr(new_connective):
                break

        LOGGER.debug("Coalesced rescoped subterms: " + repr(new_term))

        weaker = type(weaker_quantifier[0])(weaker_quantifier[0].variables, new_term)

        # Need to ensure we leave partial pre-nex in good form after rescoping
        if isinstance(new_term, Connective):
            i = 1
            scoped_term = new_term.rescope(weaker)
            while True:

                LOGGER.debug("Rescoped subterm pass #{}: {}".format(i, repr(scoped_term)))

                if isinstance(scoped_term, Connective):
                    tmp = scoped_term.rescope(weaker)
                    if (repr(tmp) == repr(scoped_term)):
                        break
                    else:
                        scoped_term = tmp
                    i = i + 1
                else:
                    break

        LOGGER.debug("YIPEEE: " + repr(scoped_term))
        LOGGER.debug("PIPEEE: " + repr(weaker))
        weaker.set_term(scoped_term)
        # Form our chosen quantifier to the top
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

    def coalesce(self):
        '''
        Coalesce or merge any like quantifiers held as terms of this
        connective. Conjunctions will coalesce Universals and will merge
        Existentials.
        '''

        obj = copy.deepcopy(self)

        existentials = [x for x in obj.terms if isinstance(x, Quantifier.Existential)]
        universals = [x for x in obj.terms if isinstance(x, Quantifier.Universal)]

        if len(universals) > 1:

            LOGGER.debug("Coalescing Universals")
            new_universal = functools.reduce(lambda x, y: x.coalesce(y), universals)

            # Ensure we rescope the internals of new quantifier
            term = new_universal.get_term()[0]
            
            #if isinstance(term, Connective):
            #    term = term.rescope(new_universal)

            new_universal.set_term(term)

            # If we only had the existentials just return the new joined one
            if len(universals) == len(obj.terms):
                return new_universal
            else:
                # Otherwise ensure we don't drop any terms
                new_terms = [x for x in obj.get_term() if x not in universals]
                new_terms.append(new_universal)

                return type(obj)(new_terms) 

        #elif len(existentials) > 1 and len(universals) == 0:
        elif len(existentials) > 1:

            LOGGER.debug("Merging nested Existentials")
            variables = []
            terms = []

            for quant in existentials:

                variables.extend(quant.variables)
                terms.extend(quant.get_term())

            exi_terms = [type(self)(terms)]
            new_existential = Quantifier.Existential(variables, exi_terms)

            # Ensure we rescope the internals of new quantifier
            term = new_existential.get_term()[0]

            if isinstance(term, Connective):
                term = term.rescope(new_existential)

            new_existential.set_term(term)
            LOGGER.debug("New Existential " + repr(new_existential))

            # If the connective only had Universals as children just return the new Universal
            if len(existentials) == len(obj.terms):
                return new_existential
            else:
                # Ensure we don't drop any terms
                leftover_terms = [x for x in obj.get_term() if x not in existentials]
                leftover_terms.append(new_existential)

                new_conjunction = Conjunction(leftover_terms)
                LOGGER.debug("Merged Conjunction: " + repr(new_conjunction))
                return new_conjunction
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

        # If our original disjunction only had two terms it's now a conjunction
        #if len(self.terms) == 2:

        #    LOGGER.debug("New Conjunction: " + repr(distributed))

        #else:
        #    # We had other terms in the disjunction, so we're still not CNF
        #    #other_terms = [x for x in working.get_term() if (x != conjunct and x != distributive_term)]
        #    LOGGER.debug("Other terms: " + repr(other_terms))
        #    LOGGER.debug(repr(distributed))

        #    # Add our freshly distributed terms to the list
        #    other_terms.append(distributed)
        #    disjunction = Disjunction(other_terms)
        #    LOGGER.debug("New Disjunction: " + repr(disjunction))

        #    return disjunction.to_onf()

    def coalesce(self):
        '''
        Coalesce or merge any like quantifiers held as terms of this
        connective. Disjunctions will coalesce existentials and will merge
        universals.
        '''

        obj = copy.deepcopy(self)

        existentials = [x for x in obj.terms if isinstance(x, Quantifier.Existential)]
        universals = [x for x in obj.terms if isinstance(x, Quantifier.Universal)]

        if len(existentials) > 1:

            LOGGER.debug("Coalescing existentials")
            new_existential = functools.reduce(lambda x, y: x.coalesce(y), existentials)

            # Ensure we rescope the internals of new quantifier
            term = new_existential.get_term()[0]
            
            #if isinstance(term, Connective):
            #    term = term.rescope(new_existential)

            new_existential.set_term(term)

            # If we only had the existentials just return the new joined one
            if len(existentials) == len(obj.terms):
                return new_existential
            else:
                # Otherwise ensure we don't drop any terms
                new_terms = [x for x in obj.get_term() if x not in existentials]
                new_terms.append(new_existential)

                return type(obj)(new_terms)

        #elif len(universals) > 1 and len(existentials) == 0:
        elif len(universals) > 1:

            LOGGER.debug("Merging nested Universals")
            variables = []
            terms = []

            for quant in universals:

                variables.extend(quant.variables)
                terms.extend(quant.get_term())

            uni_terms = [type(self)(terms)]
            new_universal = Quantifier.Universal(variables, uni_terms)

            # Ensure we rescope the internals of new quantifier
            term = new_universal.get_term()[0]
            
            if isinstance(term, Connective):
                term = term.rescope(new_universal)

            new_universal.set_term(term)
            LOGGER.debug("New Universal " + repr(new_universal))

            # If the connective only had Universals as children just return the new Universal
            if len(universals) == len(obj.terms):
                return new_universal
            else:
                # Ensure we don't drop any terms
                leftover_terms = [x for x in obj.get_term() if x not in universals]
                leftover_terms.append(new_universal)

                new_disjunction = Disjunction(leftover_terms)
                LOGGER.debug("New Disjunction: " + repr(new_disjunction))
                return new_disjunction
        else:
            return obj
