
import unittest

import macleod.logical.Symbol as Symbol
import macleod.logical.Quantifier as Quantifier

class LogicalTests(unittest.TestCase):
    '''
    Unit tests procedures for the Logical objects
    '''

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


if __name__ == '__main__':
    unittest.main()
