"""
Utility that translates Common Logic Interchange Format ontology files into
valid OWL2 XML formatted ontologies.
"""

import argparse
import logging
import sys

import macleod.parsing.Parser as Parser

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':

    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files.')
    parser.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)
    parser.add_argument('--resolve', action="store_true", help='Translate imported CLIF files', default=False)
    parser.add_argument('-b', '--dir', required='--resolve' in sys.argv, type=str, help='Base directory containing ontology files')
    parser.add_argument('-u', '--uri', required='--resolve' in sys.argv, type=str, help='URI to replace with local base path')

    # Parse the command line arguments
    args = parser.parse_args()

    # Obtain object ontology
    ontology = Parser.parse_file(args.file, args.sub, args.base, args.resolve)

    # Create a basic OWL ontology with found properties, classes, and constants
