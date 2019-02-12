#!/bash/bin/env python

import unittest

from macleod.logical.symbol import (Function, Predicate)

class SymbolTest(unittest.TestCase):

    def test_predicate_form(self):
        '''
        Ensure that predicates take the correct repr form
        '''

        alpha = Predicate('A', ['x'])
        self.assertEqual(repr(alpha), 'A(x)')

        beta = Predicate('B', ['x', 'y'])
        self.assertEqual(repr(beta), 'B(x,y)')


if __name__ == '__main__':
    unittest.main()
