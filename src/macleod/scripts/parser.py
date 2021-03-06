import argparse
import logging
import sys


LOGGER = logging.getLogger(__name__)

import macleod.parsing.parser as Parser

def main():

    LOGGER.info('Called script parse_clif')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files and print to stdout.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-p', '--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form (FF-PCNF)', default=False)
    optionalArguments.add_argument('-t', '--tptp', action='store_true', help='Convert the read axioms into TPTP format', default=False)
    optionalArguments.add_argument('-c', '--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--owl', action='store_true', help='Attempt to extract a subset OWL ontology, implies --ffpcnf', default=False)
    optionalArguments.add_argument('-b', '--base', required='--resolve' in sys.argv, type=str, help='Path to directory containing ontology files (bathpath)', default='.')
    optionalArguments.add_argument('-s', '--sub', required='--resolve' in sys.argv, type=str, help='String to replace with basepath found in imports', default='.')

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

if __name__ == '__main__':
    sys.exit(main())
