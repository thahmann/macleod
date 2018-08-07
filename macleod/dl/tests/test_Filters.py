import unittest

import macleod.dl.Filters as Filter
import macleod.dl.Patterns as Pattern
import macleod.logical.Axiom as Axiom
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol

class FiltersTest(unittest.TestCase):

    def test_can_filter_axioms(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['x'])

        simple_subclass = Axiom.Axiom(Quantifier.Universal(['x'], ~a | b))
        simple_disjoint = Axiom.Axiom(Quantifier.Universal(['x'], ~a | ~b))

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
