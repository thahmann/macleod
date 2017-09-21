import unittest

import macleod.logical.Axiom as Axiom
import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier

class LogicalTests(unittest.TestCase):
    '''
    Unit tests procedures for the Logical objects
    '''

    def test_predicate_form(self):
        '''
        Ensure that predicates take the correct repr form
        '''

        alpha = Symbol.Predicate('A', ['x'])
        self.assertEqual(repr(alpha), 'A(x)')

        beta = Symbol.Predicate('B', ['x', 'y'])
        self.assertEqual(repr(beta), 'B(x,y)')

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

    def test_negation(self):
        '''
        Ensure we can get into conjunctive normal form
        '''

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

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

        uni_one = Quantifier.Universal(['x'], alpha)
        mixer = uni_one | alpha
        uni_two = Quantifier.Universal(['y'], mixer)

        self.assertEqual(repr(uni_two), "∀(y)[(∀(x)[A(x)] | A(x))]")
        self.assertEqual(repr(uni_two.simplify()), "∀(y,x)[(A(x) | A(x))]")

    def test_cnf_quantifier_scoping(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        uni_one = Quantifier.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi_one = Quantifier.Existential(['x','y','z'], alpha & beta | delta)
        term = exi_one | beta
        term_two = exi_one | beta | uni_one

        self.assertEqual(repr(Quantifier.Universal(['x','y','z'], uni_one).simplify()), "∀(x,y,z)[(A(x) | B(y) | D(z))]")
        self.assertEqual(repr(Quantifier.Universal(['x','y','z'], term_two).simplify()), "∀(x,y,z)[(∃(x,y,z)[((A(x) & B(y)) | D(z))] | B(y) | (A(x) | B(y) | D(z)))]")
        self.assertEqual(repr(Quantifier.Universal(['x','y','z'], term_two).simplify().rescope()), "∀(x,y,z)[∃(x,y,z)[(B(y) | (A(x) | B(y) | D(z)) | ((A(x) & B(y)) | D(z)))]]")

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

    def test_onf_detection(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        uni = Quantifier.Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Quantifier.Existential(['x','y','z'], alpha & beta | delta)

        self.assertEqual(alpha.is_onf(), True)
        self.assertEqual((alpha | beta).is_onf(), True)
        self.assertEqual((alpha & beta).is_onf(), True)
        self.assertEqual((alpha | (beta & delta)).is_onf(), False)
        self.assertEqual((alpha & (beta | delta)).is_onf(), True)
        self.assertEqual((~(alpha | beta)).is_onf(), False)
        self.assertEqual((~(alpha & beta)).is_onf(), False)

        self.assertEqual(uni.is_onf(), True)
        self.assertEqual(exi.is_onf(), False)

        # Note that is_onf() is not a recursive call, it's a top level feature
        # If will actually if you need an ONF axiom then create a Logical.Axiom and to_onf()
        self.assertEqual((alpha & (alpha | (beta & delta)) & delta).is_onf(), True)

    def test_connective_to_onf(self):

        alpha = Symbol.Predicate('A', ['x'])
        beta = Symbol.Predicate('B', ['y'])
        delta = Symbol.Predicate('D', ['z'])

        one = (alpha & beta) | (delta & alpha)
        two = (beta & alpha) | (delta)
        self.assertEqual(repr(one.to_onf()), '(((D(z) & A(x)) | A(x)) & ((D(z) & A(x)) | B(y)))')
        self.assertEqual(repr(two.to_onf()), '((D(z) | B(y)) & (D(z) | A(x)))')

    def test_axiom_function_replacement(self):
        f = Symbol.Function('f', ['x'])
        t = Symbol.Function('t', ['y'])
        a = Symbol.Predicate('A', [f])
        b = Symbol.Predicate('B', [f, t])

        axi = Axiom.Axiom(Quantifier.Universal(['x'], a | a & a))
        self.assertEqual(repr(axi), '∀(x)[(A(f(x)) | (A(f(x)) & A(f(x))))]')

        axi = Axiom.Axiom(Quantifier.Universal(['x', 'y'], b))
        self.assertEqual(repr(axi.substitute_functions()), '∀(x,y)[∀(t1)[(∀(f1)[(B(f1,t1) & f(x,f1))] & t(y,t1))]]')

    def test_axiom_variable_standardize(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y', 'x'])
        c = Symbol.Predicate('C', ['a','b','c','d','e','f','g','h','i'])

        axi = Axiom.Axiom(Quantifier.Universal(['x'], a | a & a))
        self.assertEqual(repr(axi.standardize_variables()), '∀(z)[(A(z) | (A(z) & A(z)))]')

        axi = Axiom.Axiom(Quantifier.Universal(['x', 'y'], b))
        self.assertEqual(repr(axi.standardize_variables()), '∀(z,y)[B(y,z)]')

        axi = Axiom.Axiom(Quantifier.Existential(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'], c))
        self.assertEqual(repr(axi.standardize_variables()), '∃(z,y,x,w,v,u,t,s,r)[C(z,y,x,w,v,u,t,s,r)]')

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

    def test_axiom_pcnf(self):

        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y'])
        c = Symbol.Predicate('C', ['x', 'y'])

        universal = Quantifier.Universal(['x'], a)
        existential = Quantifier.Existential(['y'], b)

        derp = 
        

 














if __name__ == '__main__':
    unittest.main()
