#!/bash/bin/env python

import unittest

import macleod.logical.Axiom as Axiom
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol

class AxiomTest(unittest.TestCase):

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

    def test_axiom_to_pcnf(self):
        a = Symbol.Predicate('A', ['x'])
        b = Symbol.Predicate('B', ['y'])
        c = Symbol.Predicate('C', ['z'])

        # Simple test of disjunction over conjunction
        axi_one = Axiom.Axiom(Quantifier.Universal(['x','y','z'], a | b & c))
        axi_one = axi_one.to_pcnf()
        self.assertEqual('∀(z,y,x)[((A(z) | B(y)) & (A(z) | C(x)))]', repr(axi_one))

        # Simple sanity check, it's already FF-PCNF
        axi_two = Axiom.Axiom(Quantifier.Universal(['x','y','z'], (a | b) & c))
        axi_two = axi_two.to_pcnf()
        self.assertEqual('∀(z,y,x)[(C(x) & (A(z) | B(y)))]', repr(axi_two))

        # Sanity check we remove functions
        c = Symbol.Predicate('C', ['z', Symbol.Function('F', ['z'])])
        axi_three = Axiom.Axiom(Quantifier.Universal(['x','y','z'], a | b & c))
        axi_three = axi_three.to_pcnf()
        self.assertEqual('∀(z,y,x,w)[((A(z) | C(x,w)) & (A(z) | F(x,w)) & (A(z) | B(y)))]', repr(axi_three))
        
if __name__ == '__main__':
    unittest.main()
