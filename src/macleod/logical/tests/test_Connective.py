#!/bash/bin/env python

import unittest

from macleod.logical.connective import (Conjunction, Disjunction, Connective)
from macleod.logical.symbol import (Function, Predicate)

class ConnectiveTest(unittest.TestCase):

    def test_conjunction_form(self):
        """
        Ensure basic & operator overloading is working
        """

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['x', 'y'])
        delta = Predicate('D', ['z'])

        self.assertEqual(repr(alpha & beta), '(A(x) & B(x,y))')
        self.assertEqual(repr(alpha & beta & delta), '(A(x) & B(x,y) & D(z))')

    def test_disjunction_form(self):
        '''
        Ensure basic | operator overloading is working
        '''

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['x', 'y'])
        delta = Predicate('D', ['z'])

        self.assertEqual(repr(alpha | beta), '(A(x) | B(x,y))')
        self.assertEqual(repr(alpha | beta | delta), '(A(x) | B(x,y) | D(z))')

    def test_mixed_form(self):
        '''
        Ensure that the &  and | operators work when chained
        '''

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['x', 'y'])
        delta = Predicate('D', ['z'])

        self.assertEqual(repr((alpha & beta) | delta), '((A(x) & B(x,y)) | D(z))')
        self.assertEqual(repr(alpha & (beta | delta)), '(A(x) & (B(x,y) | D(z)))')

        self.assertEqual(repr((alpha & beta) | (alpha & delta)), '((A(x) & B(x,y)) | (A(x) & D(z)))')
        self.assertEqual(repr((alpha | beta) & (alpha | delta)), '((A(x) | B(x,y)) & (A(x) | D(z)))')

    def test_distribution(self):
        '''
        Ensure that distribution over conjunctions work
        '''
        #(b & (a | (c & b)))

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        charlie = Predicate('C', ['t'])
        delta = Predicate('D', ['z'])

        s = delta | (alpha & beta)
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '((D(z) | A(x)) & (D(z) | B(y)))')

        s = (alpha | beta) & delta 
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '((D(z) & A(x)) | (D(z) & B(y)))')

        s = (alpha | beta) & (beta | delta)
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual(repr(ret), '(((A(x) | B(y)) & B(y)) | ((A(x) | B(y)) & D(z)))')

        # Simple case - single distribute
        s = beta | (alpha & (delta | charlie))
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual('((B(y) | A(x)) & (B(y) | D(z) | C(t)))', repr(ret))

        # Slightly more complex
        s = (beta & charlie) | (alpha & (delta | charlie))
        ret = s.distribute(s.terms[0], s.terms[1])
        self.assertEqual('(((B(y) & C(t)) | A(x)) & ((B(y) & C(t)) | D(z) | C(t)))', repr(ret))

    def test_connective_to_onf(self):

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        charlie = Predicate('C', ['u'])
        delta = Predicate('D', ['z'])

        # Trivial case -- already in CNF
        two = (beta | alpha) & (delta)
        self.assertEqual(repr(two.to_onf()), '((B(y) | A(x)) & D(z))')

        two = (beta & alpha) | (delta)
        self.assertEqual(repr(two.to_onf()), '((D(z) | B(y)) & (D(z) | A(x)))')
        
        # Reversed case
        two = (delta) | (beta & alpha) 
        self.assertEqual(repr(two.to_onf()), '((D(z) | B(y)) & (D(z) | A(x)))')

        # Nested distribution
        one = (alpha & beta) | (charlie & delta)
        self.assertEqual(repr(one.to_onf()), '((A(x) | C(u)) & (A(x) | D(z)) & (B(y) | C(u)) & (B(y) | D(z)))')

        # Nested distribution
        one = (alpha | (beta & (charlie | (delta & alpha))))
        self.assertEqual(repr(one.to_onf()), '((A(x) | B(y)) & (C(u) | A(x) | D(z)) & (C(u) | A(x) | A(x)))')


if __name__ == '__main__':
    unittest.main()
