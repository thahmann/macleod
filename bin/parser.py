import argparse
import logging
import sys

from macleod.Ontology import pretty_print
import macleod.logical.Connective as Connective
import macleod.logical.Logical as Logical
import macleod.logical.Negation as Negation
import macleod.logical.Quantifier as Quantifier
import macleod.logical.Symbol as Symbol
import macleod.parsing.Parser as Parser

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':

    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files.')
    parser.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)
    parser.add_argument('-p', '--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form', default=False)
    parser.add_argument('-c', '--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)
    parser.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    parser.add_argument('-b', '--base', required='--resolve' in sys.argv, type=str, help='Path to directory containing ontology files')
    parser.add_argument('-s', '--sub', required='--resolve' in sys.argv, type=str, help='String to replace with basepath found in imports')

    # Parse the command line arguments
    args = parser.parse_args()

    # Parse out the ontology object then print it nicely
    ontology = Parser.parse_file(args.file, args.sub, args.base, args.resolve)

    for axiom in ontology.axioms:
        print (axiom)
