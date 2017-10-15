#!/bash/bin/env python

import unittest

import macleod.logical.Symbol as Symbol

class SymbolTest(unittest.TestCase):

    def test_predicate_form(self):
        '''
        Ensure that predicates take the correct repr form
        '''

        alpha = Symbol.Predicate('A', ['x'])
        self.assertEqual(repr(alpha), 'A(x)')

        beta = Symbol.Predicate('B', ['x', 'y'])
        self.assertEqual(repr(beta), 'B(x,y)')


if __name__ == '__main__':
    unittest.main()
