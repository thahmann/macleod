#!/bash/bin/env python

import unittest

import macleod.logical.Connective as Connective
import macleod.logical.Symbol as Symbol

class ConnectiveTest(unittest.TestCase):

    def test_conjunction_form(self):
        '''
        Ensure that the & operator works as intended
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['x', 'y'])
        delta = Symbol.Predicate('D', ['z'])

        self.assertEqual(repr(alpha & beta), '(A(x) & B(x,y))')
        self.assertEqual(repr(alpha & beta & delta), '(A(x) & B(x,y) & D(z))')

    def test_disjunction_form(self):
        '''
        Ensure that the & operator works as intended
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['x', 'y'])
        delta = Symbol.Predicate('D', ['z'])

        self.assertEqual(repr(alpha | beta), '(A(x) | B(x,y))')
        self.assertEqual(repr(alpha | beta | delta), '(A(x) | B(x,y) | D(z))')

    def test_mixed_form(self):
        '''
        Ensure that the & operator works as intended
        
        Note that the '&' operator has a higher precedence in python.
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['x', 'y'])
        delta = Symbol.Predicate('D', ['z'])

        self.assertEqual(repr((alpha & beta) | delta), '((A(x) & B(x,y)) | D(z))')
        self.assertEqual(repr(alpha & (beta | delta)), '(A(x) & (B(x,y) | D(z)))')

        self.assertEqual(repr((alpha & beta) | (alpha & delta)), '((A(x) & B(x,y)) | (A(x) & D(z)))')
        self.assertEqual(repr((alpha | beta) & (alpha | delta)), '((A(x) | B(x,y)) & (A(x) | D(z)))')

    def test_distribution(self):
        '''
        Ensure that distribution over conjunctions work
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        s = delta | (alpha & beta)
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '((D(z) | A(x)) & (D(z) | B(y)))')

        s = (alpha | beta) & delta 
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '((D(z) & A(x)) | (D(z) & B(y)))')

        s = (alpha | beta) & (beta | delta)
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '(((A(x) | B(y)) & B(y)) | ((A(x) | B(y)) & D(z)))')

    def test_connective_to_onf(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        one = (alpha & beta) | (delta & alpha)
        two = (beta & alpha) | (delta)
        self.assertEqual(repr(one.to_onf()), '(((D(z) & A(x)) | A(x)) & ((D(z) & A(x)) | B(y)))')
        self.assertEqual(repr(two.to_onf()), '((D(z) | B(y)) & (D(z) | A(x)))')


if __name__ == '__main__':
    unittest.main()
