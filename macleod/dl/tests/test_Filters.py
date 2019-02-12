import unittest

import macleod.dl.Filters as Filter
import macleod.dl.Patterns as Pattern
from macleod.logical.axiom import Axiom
from macleod.logical.quantifier import (Universal, Existential, Quantifier)
from macleod.logical.symbol import (Function, Predicate)

class FiltersTest(unittest.TestCase):

    def test_can_filter_axioms(self):

        a = Predicate('A', ['x'])
        b = Predicate('B', ['x'])

        simple_subclass = Axiom(Universal(['x'], ~a | b))
        simple_disjoint = Axiom(Universal(['x'], ~a | ~b))

        matching_patterns = Filter.filter_axiom(simple_subclass)
        self.assertTrue(Pattern.subclass_relation in matching_patterns)
        not_matching = Filter.filter_axiom(simple_disjoint)
        self.assertFalse(Pattern.subclass_relation in not_matching)

    def test_can_filter_on_quantifiers(self):
        pass

    def test_can_filter_on_predicates(self):
        pass

    def test_can_filter_on_variables(self):
        pass

    def test_can_filter_on_sign(self):
        pass



    

if __name__ == '__main__':
    unittest.main()
