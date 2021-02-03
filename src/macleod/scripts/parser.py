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
    optionalArguments.add_argument('-l', '--ladr', action='store_true', help='Convert the read axioms into LADR format', default=False)
    optionalArguments.add_argument('-c', '--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--owl', action='store_true', help='Attempt to extract a subset OWL ontology, implies --ffpcnf', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')

    # Parse the command line arguments
    args = parser.parse_args()

    # Parse out the ontology object then print it nicely
    default_basepath = Filemgt.get_ontology_basepath()
    if args.sub is None:
        args.sub = default_basepath[0]
    if args.base is None:
        args.base = default_basepath[1]
    ontology = Parser.parse_file(args.file, args.sub, args.base, args.resolve)

    if args.owl:
        onto = ontology.to_owl()
        print("\n-- Translation --\n")

        print(onto.tostring())

        if args.output:
            filename = write_owl_file(onto, args.resolve)
            logging.getLogger(__name__).info("Produced OWL file " + filename)


        exit(0)


    if args.ffpcnf:
        print(ontology.to_ffpcnf())

    # printing output to stdout

    if args.tptp:
        print (ontology.to_tptp(args.resolve))
    elif args.ladr:
        print (ontology.to_ladr(args.resolve))
    else:
        for axiom in ontology.axioms:
            print (axiom)

    # if output to file is also required
    if args.output:
        if args.tptp:
            filename = write_tptp_file(ontology, args.resolve)
            logging.getLogger(__name__).info("Produced TPTP file " + filename)
#        elif args.ladr:
#            print (ontology.to_ladr())
        else:
            print(ontology)

def get_output_filename(ontology, resolve, output_type):

    # the following assumes that the names of the configuration sections
    # are the same as the names of the output (tptp/ladr/owl)
    if resolve:
        ending = Filemgt.read_config(output_type, 'all_ending')
    else:
        ending = ""

    ending = ending + Filemgt.read_config(output_type, 'ending')

    output_filename = Filemgt.get_full_path(ontology.name,
                                           folder=Filemgt.read_config(output_type,'folder'),
                                           ending=ending)

    return output_filename

def write_owl_file(ontology, resolve):

    logging.getLogger(__name__).info("Approximating " + ontology.name + " as an OWL ontology")

    output_filename = get_output_filename(ontology, resolve, 'owl')

    with open(output_filename, "w") as f:
        f.write(ontology.tostring(pretty_print=True))
    f.close()

    return output_filename


def write_tptp_file(ontology, resolve):

    logging.getLogger(__name__).info("Converting " + ontology.name + " to TPTP format")

    results = ontology.to_tptp(resolve)
    # results = ontology.to_ladr(resolve)

    output_filename = get_output_filename(ontology, resolve, 'tptp')

    with open(output_filename, "w") as f:
        for sentence in results:
            print(sentence)
            f.write(sentence + "\n")
        f.close()

    return output_filename


if __name__ == '__main__':
    sys.exit(main())
