#!/bash/bin/env python

import unittest

from macleod.logical.symbol import (Function, Predicate)
from macleod.logical.quantifier import (Universal, Existential, Quantifier)

class QuantifierTest(unittest.TestCase):

    def test_quantifiers(self):

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        delta = Predicate('D', ['z'])

        uni = Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Existential(['x','y','z'], alpha & beta & delta)

        self.assertEqual(repr(uni), "∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(exi), "∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr(~uni), "~∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(~exi), "~∃(x,y,z)[(A(x) & B(y) & D(z))]")

        self.assertEqual(repr((~uni).push()), "∃(x,y,z)[~(A(x) | B(y) | D(z))]")
        self.assertEqual(repr((~exi).push()), "∀(x,y,z)[~(A(x) & B(y) & D(z))]")

    def test_cnf_quantifier_simplfy(self):

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])

        uni_one = Universal(['x'], alpha)
        mixer = uni_one | beta
        uni_two = Universal(['y'], mixer)

        uni_nested = Universal(['z'], alpha & (beta | (alpha & uni_one)))
        self.assertEqual('∀(z)[(A(x) & (B(y) | (A(x) & ∀(x)[A(x)])))]', repr(uni_nested))
        self.assertEqual('∀(z,x)[(A(x) & (B(y) | (A(x) & A(x))))]', repr(uni_nested.simplify()))

        self.assertEqual(repr(uni_two), "∀(y)[(∀(x)[A(x)] | B(y))]")
        self.assertEqual(repr(uni_two.simplify()), "∀(y,x)[(B(y) | A(x))]")

    def test_cnf_quantifier_scoping(self):

        a = Predicate('A', ['x'])
        b = Predicate('B', ['y'])
        c = Predicate('C', ['z'])

        e = Existential(['x'], a)
        u = Universal(['y'], b)

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

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        delta = Predicate('D', ['z'])

        s = ~(Universal(['x','y','z'], (~(alpha | beta) & delta)))
        self.assertEqual(repr(s.push_complete()), "∃(x,y,z)[(A(x) | B(y) | ~D(z))]")
        s = ~(Universal(['x','y','z'], ~((alpha | beta) & delta)))
        self.assertEqual(repr(s.push_complete()), "∃(x,y,z)[((A(x) | B(y)) & D(z))]")

        s = ~((~alpha | ~beta) & ~delta)
        self.assertEqual(repr(s.push_complete()), "((A(x) & B(y)) | D(z))")

        ## Test to make sure the recursino into nested stuff actually work
        s = (~~~~~~~~~alpha).push_complete()
        self.assertEqual(repr(s), '~A(x)')

        s = (~~~~~~~~alpha).push_complete()
        self.assertEqual(repr(s), 'A(x)')

    def test_axiom_connecive_rescoping(self):

        a = Predicate('A', ['x'])
        b = Predicate('B', ['y'])

        universal = Universal(['x'], a)
        existential = Existential(['y'], b)

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

        a = Predicate('A', ['x'])
        b = Predicate('B', ['y'])

        universal = Universal(['x'], a)
        universal_two = Universal(['y'], b)
        existential = Existential(['y'], b)
        existential_two = Existential(['x'], a)

        # Reduce over conjunction should coalesce Universals and merge existentials
        conjunction = universal & universal_two & existential & existential_two
        self.assertEqual(repr(conjunction.coalesce()), '(∀(x)[(B(x) & A(x))] & ∃(y,x)[(B(y) & A(x))])')

        # Reduce over disjunction should coealesce Existentials and merge Universals
        disjunction = universal | universal_two | existential | existential_two
        self.assertEqual(repr(disjunction.coalesce()), '(∃(y)[(A(y) | B(y))] | ∀(x,y)[(A(x) | B(y))])')


if __name__ == '__main__':
    unittest.main()
