import argparse
import logging
import sys, os


LOGGER = logging.getLogger(__name__)

import macleod.Filemgt
import macleod.scripts.parser as parser_script

#print(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")


default_dir = macleod.Filemgt.read_config('system', 'path')
default_prefix = macleod.Filemgt.read_config('cl', 'prefix')

def main():
    '''
    Main entry point, makes all options available
    '''

    LOGGER.info('Called script check_consistency')
    # Setup the command line arguments to the program
    parser = argparse.ArgumentParser(description='Function to check the consistency of ontologies in the Common Logic Interchange Format (.clif).')

    requiredArguments = parser.add_argument_group('required arguments')
    requiredArguments.add_argument('-f', '--file', type=str, help='Path or folder for Clif file(s) to parse', required=True)

    optionalArguments = parser.add_argument_group('optional arguments')
    optionalArguments.add_argument('-out', '--output', action='store_true', help='Write output to file', default=True)
    optionalArguments.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=False)
    optionalArguments.add_argument('--stats', action="store_true", help='Present detailed statists about the ontology', default=False)
    optionalArguments.add_argument('-n', '--nontrivial', action="store_true", default=False, help='Instantiate all predicates to check for nontrivial consistency')
    optionalArguments.add_argument('-b', '--base', default=None, type=str, help='Path to directory containing ontology files (basepath; only relevant when option --resolve is turned on; can also be set in configuration file)')
    optionalArguments.add_argument('-s', '--sub', default=None, type=str, help='String to replace with basepath found in imports, only relevant when option --resolve is turned on')

    exclusiveArguments = parser.add_mutually_exclusive_group()
    exclusiveArguments.add_argument('--simple', action='store_true', help='Do a simple consistency check', default=True)
    exclusiveArguments.add_argument('--full', action='store_true', help='Do a full resursive consistency check in case the entire ontology is not provably consistent', default=False)
    exclusiveArguments.add_argument('--module', action='store_true', help='Check each module individually', default=False)
    #exclusiveArguments.add_argument('--depth', action='store_true', help='Check with iteratively increasing depths', default=False)

    # Parse the command line arguments
    args = parser.parse_args()
    # do not need TPTP and LADR translations prior to running the reasoners; they are called as part of the command construction
    args.tptp = False
    args.ladr = False
    args.latex = False
    args.nocond = False
    args.owl = False
    args.ffpcnf = False

    # Parse out the ontology object then print it nicely
    default_basepath = macleod.Filemgt.get_ontology_basepath()
    if args.sub is None:
        args.sub = default_basepath[0]
    if args.base is None:
        args.base = default_basepath[1]

    # TODO need to substitute base path
    full_path = args.file

    if os.path.isfile(full_path):
        logging.getLogger(__name__).info("Starting to parse " + args.file)
        # Creation of the ModuleSet is from the old deprecated approach
        #m = ClifModuleSet(full_path)
        derp, clif = consistent(full_path, args)

    elif os.path.isdir(full_path):
        logging.getLogger(__name__).info("Starting to parse all CLIF files in folder " + args.file)
        # TODO need function for checking consistency of a folder
        # convert_folder(full_path, args=args)
    else:
        logging.getLogger(__name__).error("Attempted to check consistency of non-existent file or directory: " + full_path)



def consistent(filename, args):

    ontology = parser_script.convert_file(filename, args, preserve_conditionals=True)

    if args.resolve:
        ontology.resolve_imports()

    if args.stats:
        ontology.analyze_ontology()
        ontology.get_explicit_definitions()

    if args.nontrivial:
        ontology.add_nontrivial_axioms()

    if args.simple:
        # Run the parsing script first to translate to TPTP and LADR
        # as part of the args, it is communicated whether to resolve the ontology or not


        (return_value, fastest_reasoner) = ontology.check_consistency()

        if return_value == macleod.Ontology.CONSISTENT:
            if args.nontrivial:
                print(fastest_reasoner.name + " proved nontrivial consistency of " + ontology.name)
            else:
                print(fastest_reasoner.name + " proved consistency of " + ontology.name)
            print("Results saved to " + fastest_reasoner.output_file)
        exit(0)
    elif args.full:
        # TODO not yet working again
        # Run the parsing script first to translate to TPTP and LADR
        ontology = parser_script.convert_file(filename,args,preserve_conditionals=True)
        ontology.check_consistency()
        #results = m.run_full_consistency_check(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
        exit(-1)
    elif args.module:
        # TODO not yet working again
        #results = m.run_consistency_check_by_subset(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
        exit(-1)


    # the following code block is about preseting the results from multiple modules
    # if len(results)==0:
    #     logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO MODULES FOUND IN " +str(m.get_imports()) +"\n")
    # else:
    #     for (r, value, _) in results:
    #         if value==-1:
    #             logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: INCONSISTENCY FOUND IN " +str(r) +"\n")
    #             return (False, m)
    #     result_sets = [r[0] for r in results]
    #     result_sets.sort(key=lambda x: len(x))
    #     #print result_sets[0]
    #     #print results
    #     #print "+++++" + str(value)
    #     if results[0][1]==1:
    #         logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF " +str(result_sets[0]) +"\n")
    #         return (True, m)
    #     else:
    #         logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO RESULT FOR CONSISTENCY OF " +str(result_sets[0]) +"\n")
    #         if len(result_sets)>1:
    #             for (r, value, _) in results:
    #                 if value==1:
    #                     logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF SUBONTOLOGY " +str(r[0]) +"\n")
    # return (None, m)


if __name__ == '__main__':
    sys.exit(main())



