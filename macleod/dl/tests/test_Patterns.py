import unittest


import macleod.dl.Patterns as Pattern
import macleod.logical.Axiom as Axiom
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol

class PatternsTest(unittest.TestCase):

    def test_can_match_subclass_pattern(self):

        # Simple sanity check
        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['x'])

        simple = Axiom.Axiom(Quantifier.Universal(['x'], ~a | b))
        match = Pattern.subclass_relation(simple)
        self.assertIsNotNone(match)
        self.assertEqual(match[1].pop(), a)
        self.assertEqual(match[2].pop(), b)

        # Check against longer disjunctions
        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['x'])
        c = Symbol.Predicate('C', ['x'])
        d = Symbol.Predicate('D', ['x'])

        ext = Axiom.Axiom(Quantifier.Universal(['x'], ~a | ~b | c | d))
        match = Pattern.subclass_relation(ext)
        self.assertIsNotNone(match)
        self.assertEqual(match[1], [a, b])
        self.assertEqual(match[2], [c, d])

if __name__ == '__main__':
    unittest.main()
