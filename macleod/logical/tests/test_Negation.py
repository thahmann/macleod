#!/bash/bin/env python

import unittest

from macleod.logical.symbol import (Function, Predicate)

class NegationTest(unittest.TestCase):

    def test_negation(self):
        '''
        Ensure we can get into conjunctive normal form
        '''

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        delta = Predicate('D', ['z'])

        s = alpha | beta
        self.assertEqual(repr(~s), "~(A(x) | B(y))")

        s = alpha & beta
        self.assertEqual(repr(~s), "~(A(x) & B(y))")

        s = alpha & beta
        self.assertEqual(repr((~s).push()), "(~A(x) | ~B(y))")

        s = alpha | beta
        self.assertEqual(repr((~s).push()), "(~A(x) & ~B(y))")

        s = (alpha | beta) & delta
        self.assertEqual(repr((~s).push()), "(~(A(x) | B(y)) | ~D(z))")

if __name__ == '__main__':
    unittest.main()
