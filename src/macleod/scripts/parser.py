import argparse
import logging
import sys, os


LOGGER = logging.getLogger(__name__)

import macleod.parsing.parser as Parser
import macleod.Filemgt as Filemgt

default_dir = Filemgt.read_config('system', 'path')
default_prefix = Filemgt.read_config('cl', 'prefix')

def parse_clif():
    '''
    Main entry point, makes all options available
    '''

    LOGGER.info('Called script parse_clif')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Utility function to read and translate Common Logic Interchange Format (.clif) files and print to stdout.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    outputArgument = parser.add_mutually_exclusive_group()
    outputArgument.add_argument('--owl', action='store_true', help='Attempt to extract a subset OWL ontology, implies --ffpcnf', default=False)
    outputArgument.add_argument('--tptp', action='store_true', help='Convert the read axioms into TPTP format', default=False)
    outputArgument.add_argument('--ladr', action='store_true', help='Convert the read axioms into LADR format', default=False)
    outputArgument.add_argument('--latex', action='store_true', help='Convert the read axioms into LaTeX format', default=False)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('--enum', action='store_true', help='Enumerate axioms in LaTeX output', default=False)
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--nocond', action='store_true', help='Do not use conditionals (only applies to TPTP, LADR and LaTeX production)', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')
    optionalArguments.add_argument('--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form (FF-PCNF)', default=False)
    optionalArguments.add_argument('--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)

    # Parse the command line arguments
    args = parser.parse_args()

    main(args)

def clif_to_tptp():
    '''
    Script to translate to TPTP
    :return:
    '''
    LOGGER.info('Called script parse_clif')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Read Common Logic Interchange Format (.clif) files and convert to TPTP format.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--nocond', action='store_true', help='Do not use conditionals (only applies to TPTP, LADR and LaTeX production)', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')

    # Parse the command line arguments
    args = parser.parse_args()
    args.tptp = True
    args.ladr = False
    args.latex = False
    args.owl = False
    args.ffpcnf = False
    main(args)

def clif_to_ladr():
    '''
    Script to translate to LADR
    :return:
    '''
    LOGGER.info('Called script clif_to_ladr')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Read Common Logic Interchange Format (.clif) files and convert to LADR format.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--nocond', action='store_true', help='Do not use conditionals (only applies to TPTP, LADR and LaTeX production)', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')

    # Parse the command line arguments
    args = parser.parse_args()
    args.ladr = True
    args.tptp = False
    args.latex = False
    args.owl = False
    args.ffpcnf = False
    main(args)

def clif_to_owl():
    '''
    Script to translate to LADR
    :return:
    '''
    LOGGER.info('Called script clif_to_ladr')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Read Common Logic Interchange Format (.clif) files and approximate them by OWL ontologies.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')
    optionalArguments.add_argument('--ffpcnf', action='store_true', help='Automatically convert axioms to function-free prenex conjuntive normal form (FF-PCNF)', default=False)
    optionalArguments.add_argument('--clip', action='store_true', help='Split FF-PCNF axioms across the top level quantifier', default=False)

    # Parse the command line arguments
    args = parser.parse_args()
    args.owl = True
    args.ladr = False
    args.tptp = False
    args.latex = False
    main(args)

def clif_to_latex():
    '''
    Script to translate to LaTeX
    :return:
    '''
    LOGGER.info('Called script parse_clif')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Read Common Logic Interchange Format (.clif) files and convert to LaTeX format.')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--enum', action='store_true', help='Enumerate axioms in LaTeX output', default=False)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')

    # Parse the command line arguments
    args = parser.parse_args()
    args.latex = True
    args.nocond = False
    args.tptp = False
    args.ladr = False
    args.owl = False
    args.ffpcnf = False
    main(args)


def main(args):
    '''

    :param args: arguments passed from customized entry points
    :return:
    '''

    # Parse out the ontology object then print it nicely
    default_basepath = Filemgt.get_ontology_basepath()
    if args.sub is None:
        args.sub = default_basepath[0]
    if args.base is None:
        args.base = default_basepath[1]

    if (args.tptp or args.ladr or args.latex) and args.nocond is False:
        Parser.conditionals = True

    # TODO need to substitute base path
    full_path = args.file

    if os.path.isfile(full_path):
        logging.getLogger(__name__).info("Starting to parse " + args.file)
        convert_file(full_path, args=args)

    elif os.path.isdir(full_path):
        logging.getLogger(__name__).info("Starting to parse all CLIF files in folder " + args.file)
        convert_folder(full_path, args=args)
    else:
        logging.getLogger(__name__).error("Attempted to parse non-existent file or directory: " + full_path)


def convert_file(file, args):

    ontology = Parser.parse_file(file, args.sub, args.base, args.resolve, preserve_conditionals = not(args.ffpcnf))

    if ontology is None:
        # some error occured while parsing CLIF file(s)
        exit(-1)

    # producing OWL output
    if args.owl:
        onto = ontology.to_owl()

        print("\n-- Translation --\n")
        print(onto.tostring())

        if args.output:
            # producing OWL file
            filename = ontology.write_owl_file()
            logging.getLogger(__name__).info("Produced OWL file " + filename)

    # producing TPTP ouput
    elif args.tptp:

        print(ontology.to_tptp())

        if args.output:
            filename = ontology.write_tptp_file()
            logging.getLogger(__name__).info("Produced TPTP file " + filename)
            return filename


    # producing LADR output
    elif args.ladr:

        print(ontology.to_ladr())

        if args.output:
            filename = ontology.write_ladr_file()
            logging.getLogger(__name__).info("Produced LADR file " + filename)
            return filename

    # producing LaTeX output
    elif args.latex:
        if args.output:
            filename = ontology.write_latex_file(args.enum)
            logging.getLogger(__name__).info("Produced LaTeX file " + filename)
            return filename
        else:
            print(ontology.to_latex())

    # Just converting to Function-free Prenex-Conjunctive-Normalform
    elif args.ffpcnf:
        print(ontology.to_ffpcnf())

    return ontology


def convert_folder(folder, args):

    tempfolder = Filemgt.read_config('converters', 'tempfolder')
    ignores = [tempfolder]
    cl_ending = Filemgt.read_config('cl', 'ending')
    #logging.getLogger(__name__).info("Traversing folder " + folder)

    for directory, subdirs, files in os.walk(folder):
        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                if single_file.endswith(cl_ending):
                    file = os.path.join(directory, single_file)
                    logging.getLogger(__name__).info("Parsing CLIF file " + file)
                    convert_file(file, args=args)


if __name__ == '__main__':
    sys.exit(main())
