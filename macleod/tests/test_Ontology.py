import unittest

from macleod.logical.symbol import (Function, Predicate)
from macleod.logical.axiom import Axiom
from macleod.logical.quantifier import (Universal, Existential, Quantifier)
import macleod.Ontology as Ontology

class OnologyTest(unittest.TestCase):
    """
    Test functionality of Ontology class
    """

    def test_owl_subclass(self):
        a = Predicate('A', ['x'])
        b = Predicate('B', ['x'])
        c = Predicate('C', ['x'])
        d = Predicate('D', ['x'])
        subclass_relation = Axiom(Universal(['x'],  ~d | b | c))

        onto = Ontology("Derp")
        onto.axioms.append(subclass_relation)
        print(onto.to_owl())

if __name__ == '__main__':
    unittest.main()
