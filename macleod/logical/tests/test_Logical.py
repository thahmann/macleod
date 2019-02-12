
import unittest

from macleod.logical.symbol import (Function, Predicate)
from macleod.logical.quantifier import (Universal, Existential, Quantifier)

class LogicalTests(unittest.TestCase):
    '''
    Unit tests procedures for the Logical objects
    '''

    def test_onf_detection(self):

        alpha = Predicate('A', ['x'])
        beta = Predicate('B', ['y'])
        delta = Predicate('D', ['z'])

        uni = Universal(['x', 'y', 'z'], alpha | beta | delta)
        exi = Existential(['x','y','z'], alpha & beta | delta)

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
        self.assertEqual((alpha & (alpha | (beta & delta)) & delta).is_onf(), False)


if __name__ == '__main__':
    unittest.main()
