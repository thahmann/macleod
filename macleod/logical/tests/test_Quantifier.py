#!/bash/bin/env python

import unittest

import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier

class QuantifierTest(unittest.TestCase):

    def test_quantifiers(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        uni = Quantifier.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Quantifier.Existential(['x','y','z'], alpha & beta & delta)

        self.assertEqual(repr(uni), "∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(exi), "∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr(~uni), "~∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(~exi), "~∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr((~uni).push()), "∃(x,y,z)[~(A(x) | B(y) | D(z))]")
        self.assertEqual(repr((~exi).push()), "∀(x,y,z)[~(A(x) & B(y) & D(z))]")

    def test_cnf_quantifier_simplfy(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])

        uni_one = Quantifier.Universal(['x'], alpha)
        mixer = uni_one | beta
        uni_two = Quantifier.Universal(['y'], mixer)

        uni_nested = Quantifier.Universal(['z'], alpha & (beta | (alpha & uni_one)))
        self.assertEqual('∀(z)[(A(x) & (B(y) | (A(x) & ∀(x)[A(x)])))]', repr(uni_nested))
        self.assertEqual('∀(z,x)[(A(x) & (B(y) | (A(x) & A(x))))]', repr(uni_nested.simplify()))

        self.assertEqual(repr(uni_two), "∀(y)[(∀(x)[A(x)] | B(y))]")
        self.assertEqual(repr(uni_two.simplify()), "∀(y,x)[(B(y) | A(x))]")

    def test_cnf_quantifier_scoping(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y'])
        c = Symbol.Predicate('C', ['z'])

        e = Quantifier.Existential(['x'], a)
        u = Quantifier.Universal(['y'], b)

        # Test the effect over an OR
        self.assertEqual('∃(x)[(A(x) | B(y))]', repr((e | b).rescope()))
        self.assertEqual('∀(y)[(B(y) | A(x))]', repr((u | a).rescope()))

        # Test the effect over an AND
        self.assertEqual('∃(x)[(A(x) & B(y))]', repr((e & b).rescope()))
        self.assertEqual('∀(y)[(B(y) & A(x))]', repr((u & a).rescope()))

        # Test with more than two to make sure things aren't dropped
        self.assertEqual('∀(y)[(B(y) & (A(x) | C(z) | B(y)))]', repr((u & (a | c | b)).rescope()))


    def test_cnf_negation(self):
        '''
        Ensure we can get into conjunctive normal form
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        s = ~(Quantifier.Universal(['x','y','z'], (~(alpha | beta) & delta)))
        self.assertEqual(repr(s.push_complete()), "∃(x,y,z)[(A(x) | B(y) | ~D(z))]")
        s = ~(Quantifier.Universal(['x','y','z'], ~((alpha | beta) & delta)))
        self.assertEqual(repr(s.push_complete()), "∃(x,y,z)[((A(x) | B(y)) & D(z))]")

        s = ~((~alpha | ~beta) & ~delta)
        self.assertEqual(repr(s.push_complete()), "((A(x) & B(y)) | D(z))")

        ## Test to make sure the recursino into nested stuff actually work
        s = (~~~~~~~~~alpha).push_complete()
        self.assertEqual(repr(s), '~A(x)')

        s = (~~~~~~~~alpha).push_complete()
        self.assertEqual(repr(s), 'A(x)')

    def test_axiom_connecive_rescoping(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y'])

        universal = Quantifier.Universal(['x'], a)
        existential = Quantifier.Existential(['y'], b)

        conjunction = universal & existential
        disjunction = universal | existential

        # Ensure we handle single quantifier case
        self.assertEqual(repr((universal & b).rescope()), '∀(x)[(A(x) & B(y))]')
        self.assertEqual(repr((existential & a).rescope()), '∃(y)[(B(y) & A(x))]')
        self.assertEqual(repr((universal | b).rescope()), '∀(x)[(A(x) | B(y))]')
        self.assertEqual(repr((existential | a).rescope()), '∃(y)[(B(y) | A(x))]')

        # Ensure we catch error condition where lookahead is needed
        self.assertRaises(ValueError, (existential | universal).rescope)

        # Ensure that we can promote Universals when a conjunction lives above us
        top = a & disjunction
        self.assertEqual(repr(disjunction.rescope(top)), '∀(x)[∃(y)[(A(x) | B(y))]]')

        # Ensure that we can promote Existentials when a conjunction lives above us
        top = a | conjunction 
        self.assertEqual(repr(conjunction.rescope(top)), '∃(y)[∀(x)[(B(y) & A(x))]]')

    def test_axiom_quantifier_coalesence(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y'])

        universal = Quantifier.Universal(['x'], a)
        universal_two = Quantifier.Universal(['y'], b)
        existential = Quantifier.Existential(['y'], b)
        existential_two = Quantifier.Existential(['x'], a)

        # Coalescence over conjunction should merge Universals
        conjunction = universal & universal_two & existential & existential_two
        self.assertEqual(repr(conjunction.coalesce()), '(∃(y)[B(y)] & ∃(x)[A(x)] & ∀(x)[(B(x) & A(x))])')

        # Coalescence over disjunction should merge Existentials
        disjunction = universal | universal_two | existential | existential_two
        self.assertEqual(repr(disjunction.coalesce()), '(∀(x)[A(x)] | ∀(y)[B(y)] | ∃(y)[(A(y) | B(y))])')


if __name__ == '__main__':
    unittest.main()
