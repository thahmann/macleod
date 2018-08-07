#!/usr/bin/env python

"""
Module that processes Logical objects into OWL objects.

Functionality wise this module searches through the Logical objects that
represent first-order logic (FOL) axioms and attempts to identify a suitable
Web Ontology Language (OWL) translation. Not all axioms are guaranteed a
translation and even if an axiom has some valid translation there is no
guarantee that it will be identified. These pattern identification algorithms
are best effort, though in practice they work successfully a majority of the
time.
"""

import macleod.dl.Utilities as Utility

def translate_owl(axioms):
    """
    Accepts a list of axioms and returns an Ontology object containing
    all the extracted OWL constructs.

    :param list axioms, list of axioms
    :return owlready.Ontology onto
    """

    for axiom in axioms:

        ff_pcnf = axiom.ff_pcnf()
        logicals = []
        Utility.split_logical(ff_pcnf, logical, [], [], [])

        for logical in logicals:

            pruned_logical = Utility.prune_prenex(logical)

