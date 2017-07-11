import unittest
import Logical

class LogicalTests(unittest.TestCase):
    '''
    Unit tests procedures for the Logical objects
    '''

    def test_predicate_form(self):
        '''
        Ensure that predicates take the correct repr form
        '''

        alpha = Logical.Predicate('A', ['x'])
        self.assertEqual(repr(alpha), 'A(x)')

        beta = Logical.Predicate('B', ['x', 'y'])
        self.assertEqual(repr(beta), 'B(x,y)')

    def test_conjunction_form(self):
        '''
        Ensure that the & operator works as intended
        '''

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['x', 'y'])
        delta = Logical.Predicate('D', ['z'])

        self.assertEqual(repr(alpha & beta), '(A(x) & B(x,y))')
        self.assertEqual(repr(alpha & beta & delta), '(A(x) & B(x,y) & D(z))')

    def test_disjunction_form(self):
        '''
        Ensure that the & operator works as intended
        '''

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['x', 'y'])
        delta = Logical.Predicate('D', ['z'])

        self.assertEqual(repr(alpha | beta), '(A(x) | B(x,y))')
        self.assertEqual(repr(alpha | beta | delta), '(A(x) | B(x,y) | D(z))')

    def test_mixed_form(self):
        '''
        Ensure that the & operator works as intended
        
        Note that the '&' operator has a higher precedence in python.
        '''

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['x', 'y'])
        delta = Logical.Predicate('D', ['z'])

        self.assertEqual(repr((alpha & beta) | delta), '((A(x) & B(x,y)) | D(z))')
        self.assertEqual(repr(alpha & (beta | delta)), '(A(x) & (B(x,y) | D(z)))')

        self.assertEqual(repr((alpha & beta) | (alpha & delta)), '((A(x) & B(x,y)) | (A(x) & D(z)))')
        self.assertEqual(repr((alpha | beta) & (alpha | delta)), '((A(x) | B(x,y)) & (A(x) | D(z)))')

    def test_distribution(self):
        '''
        Ensure that distribution over conjunctions work
        '''

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['y'])
        delta = Logical.Predicate('D', ['z'])

        s = delta | (alpha & beta)
        self.assertEqual(repr(s.distribute(s.terms[0], s.terms[1])), '((D(z) | A(x)) & (D(z) | B(y)))')

        s = (alpha | beta) & delta 
        self.assertEqual(repr(s.distribute(s.terms[0], s.terms[1])), '((D(z) & A(x)) | (D(z) & B(y)))')

        s = (alpha | beta) & (beta | delta)
        self.assertEqual(repr(s.distribute(s.terms[0], s.terms[1])), '(((A(x) | B(y)) & B(y)) | ((A(x) | B(y)) & D(z)))')

    def test_negation(self):
        '''
        Ensure we can get into conjunctive normal form
        '''

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['y'])
        delta = Logical.Predicate('D', ['z'])

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

    def test_quantifiers(self):

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['y'])
        delta = Logical.Predicate('D', ['z'])

        uni = Logical.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Logical.Existential(['x','y','z'], alpha & beta & delta)

        self.assertEqual(repr(uni), "∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(exi), "∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr(~uni), "~∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(~exi), "~∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr((~uni).push()), "∃(x,y,z)[~(A(x) | B(y) | D(z))]")
        self.assertEqual(repr((~exi).push()), "∀(x,y,z)[~(A(x) & B(y) & D(z))]")

    def test_cnf_detection(self):

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['y'])
        delta = Logical.Predicate('D', ['z'])

        uni = Logical.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Logical.Existential(['x','y','z'], alpha & beta | delta)

        self.assertEqual(alpha.is_cnf(), True)
        self.assertEqual((alpha | beta).is_cnf(), True)
        self.assertEqual((alpha & beta).is_cnf(), True)
        self.assertEqual((alpha | (beta & delta)).is_cnf(), False)
        self.assertEqual((alpha & (beta | delta)).is_cnf(), True)
        self.assertEqual((~(alpha | beta)).is_cnf(), False)
        self.assertEqual((~(alpha & beta)).is_cnf(), False)

        self.assertEqual(uni.is_cnf(), True)
        self.assertEqual(exi.is_cnf(), False)

        self.assertEqual((alpha & (alpha | (beta & delta)) & delta).is_cnf(), False)

    def test_cnf_quantifier_scoping(self):

        alpha = Logical.Predicate('A', ['x'])
        beta = Logical.Predicate('B', ['y'])
        delta = Logical.Predicate('D', ['z'])

        uni_one = Logical.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi_one = Logical.Existential(['x','y','z'], alpha & beta | delta)
        term = exi_one | beta
        term_two = exi_one | beta | uni_one

        self.assertEqual(repr(Logical.Universal(['x','y','z'], term_two).rescope()), "")
        self.assertEqual(repr(Logical.Universal(['x','y','z'], term).rescope()), "")




if __name__ == '__main__':
    unittest.main()
