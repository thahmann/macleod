import argparse
import logging
import sys


LOGGER = logging.getLogger(__name__)

import macleod.parsing.parser as Parser
import macleod.Filemgt as Filemgt

default_dir = Filemgt.read_config('system', 'path')
default_prefix = Filemgt.read_config('cl', 'prefix')

def main():

    LOGGER.info('Called script parse_clif')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files and print to stdout.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-o', '--output', action='store_true', help='Write output to file', default=False)
    optionalArguments.add_argument('-p', '--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form (FF-PCNF)', default=False)
    optionalArguments.add_argument('-t', '--tptp', action='store_true', help='Convert the read axioms into TPTP format', default=False)
    #optionalArguments.add_argument('-l', '--ladr', action='store_true', help='Convert the read axioms into LADR format', default=False)
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

        print(onto.tostring())
        exit(0)


    if args.ffpcnf:
        print(ontology.to_ffpcnf())

    # printing output to stdout
    for axiom in ontology.axioms:

        if args.tptp:
            print (axiom.to_tptp())
 #       elif args.ladr:
 #           print (axiom.to_ladr())
        else:
            print (axiom)

    # if output to file is also required
    if args.output:
        if args.tptp:
            filename = write_tptp_file(ontology, args.resolve)
            logging.getLogger(__name__).info("Finished writing TPTP file " + filename)
#        elif args.ladr:
#            print (ontology.to_ladr())
        else:
            print(ontology)


def write_tptp_file(ontology, resolve, loc=default_dir, prefix=default_prefix):

    logging.getLogger(__name__).info("Converting " + ontology.name + " to TPTP format")

    results = ontology.to_tptp(resolve)
    # results = ontology.to_ladr(resolve)

    # the following assumes that the names of the configuration sections are the same as the names of the output (tptp/ladr)
    if resolve:
        ending = Filemgt.read_config('tptp', 'all_ending')
    else:
        ending = ""

    ending = ending + Filemgt.read_config('tptp', 'ending')

    output_file_name = Filemgt.get_full_path(ontology.name,
                                           folder=Filemgt.read_config('tptp','folder'),
                                           ending=ending)

    with open(output_file_name, "w") as f:
        for sentence in results:
            print(sentence)
            f.write(sentence + "\n")
        f.close()

    return output_file_name


if __name__ == '__main__':
    sys.exit(main())
