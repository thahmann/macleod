import argparse
import logging
import sys

LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

import macleod.parsing.parser as Parser

if __name__ == '__main__':

    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files and print to stdout.')
    parser.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)
    parser.add_argument('-p', '--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form', default=False)
    parser.add_argument('-t', '--tptp', action='store_true', help='Convert the read axioms into TPTP format', default=False)
    parser.add_argument('-c', '--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)
    parser.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    parser.add_argument('--owl', action='store_true', help='Attempt to extract a subset OWL ontology, implies --ffpcnf', default=False)
    parser.add_argument('-b', '--base', required='--resolve' in sys.argv, type=str, help='Path to directory containing ontology files')
    parser.add_argument('-s', '--sub', required='--resolve' in sys.argv, type=str, help='String to replace with basepath found in imports')

    # Parse the command line arguments
    args = parser.parse_args()

    # Parse out the ontology object then print it nicely
    ontology = Parser.parse_file(args.file, args.sub, args.base, args.resolve)

    if args.owl:
        onto = ontology.to_owl()
        print("\n-- Translation --\n")
        print(onto)
        exit(0)


    if args.ffpcnf:
        ontology.to_ffpcnf()

    for axiom in ontology.axioms:

        if args.tptp:
            print (axiom.to_tptp())
        else:
            print (axiom)



