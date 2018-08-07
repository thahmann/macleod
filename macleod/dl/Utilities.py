import collections
import copy
import logging

import macleod.logical.Quantifier as Quantifier
import macleod.logical.Connective as Connective
import macleod.logical.Symbol as Symbol
import macleod.logical.Negation as Negation

LOGGER = logging.getLogger(__name__)

def split_logical(logical, axioms, prenex, u_vars, e_vars):
    """
    Splits a logical across conjuncts and returns list of new logicals with the
    approriate prenexes. This operation maintains logical equivalency of the
    splits and their original conjunction. Note that this means some
    conjunctions cannot be split

    param: Logical logical, a FF-PCNF logical to be split
    param: List axioms, accumulator for resulting split logicals
    param: List prenex, accumulator for recursion
    param: List u_vars, accumulator for recursion
    param: List e_vars, accumulator for recursion
    """

    if isinstance(logical, Quantifier.Quantifier):
        LOGGER.debug("Adding to the quantifier")

        prenex.append(logical)

        if len(e_vars) > 0:
            # Variables within the scope of an existential limit splitting
            e_vars.extend(logical.variables)

        elif isinstance(logical, Quantifier.Universal):
            u_vars.extend(logical.variables)

        elif isinstance(logical, Quantifier.Existential):
            # Entered existential scoping :(
            e_vars.extend(logical.variables)

        split_logical(logical.get_term()[0], axioms,  prenex, u_vars, e_vars)

    elif isinstance(logical, Connective.Connective):

        if isinstance(logical, Connective.Disjunction):

            # We could only split if we're under a single existential
            # but in this case it'd be at top level axioms so splitting makes no sense
            return

        else:

            # Time to look through the children
            for conjunct in logical.get_term():

                # Short circuit flag
                ditch = False

                if isinstance(conjunct, Symbol.Predicate) or isinstance(conjunct, Negation.Negation):

                    # Ignore if the predicate is negated or not
                    term = conjunct if isinstance(conjunct, Symbol.Predicate) else conjunct.get_term()[0]
                    
                    for var in term.variables:
                        # If we have a single term with e_vars scrap this conjunct
                        if var in e_vars:
                            ditch = True
                            break

                    if ditch:
                        break

                    if ditch == False:

                        # This conjunct has only u_vars! Mark it for splitting
                        axioms.append(conjunct)


                for term in conjunct.get_term():

                    # Ignore if the predicate is negated or not
                    term = term if isinstance(term, Symbol.Predicate) else term.get_term()[0]
                    
                    for var in term.variables:
                        # If we have a single term with e_vars scrap this conjunct
                        if var in e_vars:
                            ditch = True
                            break

                    if ditch:
                        break

                if ditch == False:

                    # This conjunct has only u_vars! Mark it for splitting
                    axioms.append(conjunct)

        # Remember to grab the remaining conjuncts that couldn't be split off
        others = [conjunct for conjunct in logical.get_term() if conjunct not in axioms]

        # Form them into their own separate Conjunction
        if len(others) == 1:
            axioms.append(others.pop())
        elif len(others) > 1:
            logical = Connective.Conjunction(others)
            axioms.append(logical)
    else:

        LOGGER.info("Hit a single quantified predicate, dumb, but I'll split it")
        axioms.append(logical)

def prenex_parser(logical, prenex, parent):
    """
    DFS through a prenex accumulating each quantifier in the [prenex] list.
    Order is important.
    """

    if isinstance(logical, Quantifier.Quantifier):
        LOGGER.debug("Adding to the quantifier")

        prenex.append(logical)
        prenex_parser(logical.get_term()[0], prenex, logical)

    else:

        # Hit the bottom of the prenex, insert a dummy Predicate
        null = Symbol.Predicate("Null", ['null'])

        if parent is not None:
            parent.set_term(null)

        return

def prune_prenex(log, pruned):
    """
    Accepts a conjunction and sub-term for which the prenex should be pruned. 
    Has no side effects and returns copies of the passed in Logicals.

    :param Logical.Logical log, the containing conjunct
    :param Logical.Logical pruned, a sub-term of the conjunct
    :return Logical.Logical prune
    """

    logical = copy.deepcopy(log)
    pruned_conjunct = copy.deepcopy(pruned)

    # Set our accessible list of quantifiers
    prenex = []
    prenex_parser(logical, prenex, None)

    seen_variables = set()

    # Edge condition, the pruned_conjunct is jut a single predicate
    if isinstance(pruned_conjunct, Symbol.Predicate) or isinstance(pruned_conjunct, Negation.Negation):

        term = pruned_conjunct if isinstance(pruned_conjunct, Symbol.Predicate) else pruned_conjunct.get_term()[0]
        seen_variables.update(term.variables)

    # We have a Connective to iterate through
    else:

        for term in pruned_conjunct.get_term():
            
            # Expected case have a conjunction or disjunction of predicates
            if isinstance(term, Symbol.Predicate) or isinstance(term, Negation.Negation):
                term = term if isinstance(term, Symbol.Predicate) else term.get_term()[0]
                seen_variables.update(term.variables)
            
            # Edge case, we have a conjunction of disjunctions as the pruned conjunct
            else:
                for atom in term.get_term():
                    atom = atom if isinstance(atom, Symbol.Predicate) else atom.get_term()[0]
                    seen_variables.update(atom.variables)

    LOGGER.debug("Pruned Conjunct:" + repr(pruned_conjunct))
    LOGGER.debug("Observed Variables: " + str(seen_variables))
    LOGGER.debug("Starting Prenex: " + str(prenex))
    
    remove_bin = []
    for idx, quantifier in enumerate(prenex):

        new_variables = set(quantifier.variables)
        LOGGER.debug("Seen Variables: " + str(seen_variables) + " Current Variables: " + str(new_variables))
        new_variables = new_variables.intersection(seen_variables)
        quantifier.variables = list(new_variables)

        # Our conjunct wasn't scoped in this variable, safely remove it
        if len(quantifier.variables) == 0:

            to_remove = prenex[idx]
            LOGGER.debug("Removing Quantifier: " + str(to_remove))
            parent_quantifier = prenex[idx-1]
            parent_quantifier.set_term(to_remove.get_term())
            remove_bin.append(to_remove)

    for unused_quant in remove_bin:
        prenex.remove(unused_quant)

    prenex[-1].set_term(pruned_conjunct)

    new_axiom = prenex[0]
    LOGGER.debug("Pruned Axiom: " + repr(new_axiom))
    return new_axiom

def term_parser(logical):
    """
    DFS through a prenex to get to the nested term. Returns the first logical
    that isn't a quantifier.

    Expects: This operation is happening on a FF-PCNF logical
    returns: Logical term, a term that isn't a quantifier
    """

    if isinstance(logical, Quantifier.Quantifier):

        term_parser(logical.get_term()[0])

    else:

        return logical
