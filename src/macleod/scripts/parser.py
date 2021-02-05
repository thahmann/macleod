import argparse
import logging
import sys, os


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
    optionalArguments.add_argument('--owl', action='store_true', help='Attempt to extract a subset OWL ontology, implies --ffpcnf', default=False)
    optionalArguments.add_argument('--tptp', action='store_true', help='Convert the read axioms into TPTP format', default=False)
    optionalArguments.add_argument('--ladr', action='store_true', help='Convert the read axioms into LADR format', default=False)
    optionalArguments.add_argument('--latex', action='store_true', help='Convert the read axioms into LaTeX format', default=False)
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

    # Parse out the ontology object then print it nicely
    default_basepath = Filemgt.get_ontology_basepath()
    if args.sub is None:
        args.sub = default_basepath[0]
    if args.base is None:
        args.base = default_basepath[1]
    logging.getLogger(__name__).info("Starting to parse " + args.file)

    if (args.tptp or args.ladr or args.latex) and args.nocond is False:
        Parser.conditionals = True
    ontology = Parser.parse_file(args.file, args.sub, args.base, args.resolve)

    if ontology is None:
        exit(-1)

    # producing OWL output
    if args.owl:
        onto = ontology.to_owl()
        print("\n-- Translation --\n")

        print(onto.tostring())

        # producing OWL file
        if args.output:
            filename = write_owl_file(onto, args.resolve)
            logging.getLogger(__name__).info("Produced OWL file " + filename)

        exit(0)

    if args.tptp:
        to_tptp(ontology, args.resolve, args.output)

    if args.ladr:
        to_ladr(ontology, args.resolve, args.output)

    if args.latex:
        to_latex(ontology, args.resolve, args.output, args.enum)

    if args.ffpcnf:
        print(ontology.to_ffpcnf())



def to_tptp(ontology, resolve=False, output=True):
    # printing output to stdout
    print(ontology.to_tptp(resolve))
    if output:
        filename = write_tptp_file(ontology, resolve)
        logging.getLogger(__name__).info("Produced TPTP file " + filename)


def to_ladr(ontology, resolve=False, output=True):
    # printing output to stdout
    print(ontology.to_ladr(resolve))
    if output:
        filename = write_ladr_file(ontology, resolve)
        logging.getLogger(__name__).info("Produced LADR file " + filename)


def to_latex(ontology, resolve=False, output=True, enumerate=False):
    # printing output to stdout
    print(ontology.to_latex(resolve))
    if output:
        filename = write_latex_file(ontology, resolve, enumerate)
        logging.getLogger(__name__).info("Produced LaTeX file " + filename)



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

    output_filename = get_output_filename(ontology, resolve, 'tptp')

    with open(output_filename, "w") as f:
        for sentence in results:
            print(sentence)
            f.write(sentence + "\n")
        f.close()

    return output_filename

def write_ladr_file(ontology, resolve):

    logging.getLogger(__name__).info("Converting " + ontology.name + " to LADR format")

    results = ontology.to_ladr(resolve)

    output_filename = get_output_filename(ontology, resolve, 'ladr')

    with open(output_filename, "w") as f:
        if len(results) > 0:
            f.write("formulas(sos).\n")
            for sentence in results:
                print(sentence)
                f.write(sentence + "\n")
            f.write("end_of_list.\n")
        f.close()

    return output_filename

def write_latex_file(ontology, resolve, enumerate):

    logging.getLogger(__name__).info("Converting " + ontology.name + " to LaTeX format")

    results = ontology.to_latex(resolve)

    output_filename = get_output_filename(ontology, resolve, 'latex')


    with open(output_filename, "w") as f:
        f.write("\\documentclass{article}\n")

        f.write("\\usepackage{amsmath,amssymb,hyperref}\n\n")
        f.write("\\delimitershortfall = -0.5pt\n\n")

        printable_name = ontology.name.replace(os.sep, '/').replace("_","\_")

        f.write("\\begin{document}\n")
        f.write("\\textbf{\\url{"+ printable_name +"}}\n\n")
        if enumerate:
            f.write("\\begin{enumerate}\n")
        for sentence in results:
            print(sentence)
            if enumerate:
                f.write("\\item " + sentence + "\n")
            else:
                f.write(sentence + "\n\n")
        if enumerate:
            f.write("\\end{enumerate}\n")
        f.write("\\end{document}")
        f.close()

    return output_filename


if __name__ == '__main__':
    sys.exit(main())
