import unittest

from macleod.logical.axiom import Axiom
from macleod.logical.quantifier import (Universal, Existential, Quantifier)
from macleod.logical.symbol import (Function, Predicate)

import macleod.dl.patterns as Pattern

class PatternsTest(unittest.TestCase):

    def test_can_match_subclass_pattern(self):

        # Simple sanity check
        a = Predicate('A', ['x'])
        b = Predicate('B', ['x'])

        simple = Axiom(Universal(['x'], ~a | b))
        match = Pattern.subclass_relation(simple)
        self.assertIsNotNone(match)
        self.assertEqual(match[1].pop(), a)
        self.assertEqual(match[2].pop(), b)

        # Check against longer disjunctions
        a = Predicate('A', ['x'])
        b = Predicate('B', ['x'])
        c = Predicate('C', ['x'])
        d = Predicate('D', ['x'])

        ext = Axiom(Universal(['x'], ~a | ~b | c | d))
        match = Pattern.subclass_relation(ext)
        self.assertIsNotNone(match)
        self.assertEqual(match[1], [a, b])
        self.assertEqual(match[2], [c, d])

if __name__ == '__main__':
    unittest.main()
