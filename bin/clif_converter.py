'''
Created on 2019-03-07

@author: Torsten Hahmann
'''

import os, sys, argparse, logging

#print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")


from bin import licence
import macleod.Filemgt as Filemgt
import macleod.parsing.Parser as Parser
#from macleod.Filemgt import Filemgt



if __name__ == '__main__':
    licence.print_terms()
    
    # defaults for the ontology directory and basepath
    default_dir = Filemgt.read_config('system','path')
    default_prefix = Filemgt.read_config('cl','prefix')
    tptp_output = 'tptp'
    ladr_output = 'ladr'

    # global variables
    parser = argparse.ArgumentParser(description='Utility function to convert Common Logic Interchange Format (.clif) files to the TPTP or LADR syntax.')
    parser.add_argument('-f', '--file', type=str, help='Clif file to parse', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output format', default=tptp_output)
    parser.add_argument('-n', '--noresolve', action="store_false", help='Prevent from automatically resolving imports', default=True)
    parser.add_argument('--loc', type=str, help='Path to directory containing ontology files', default=default_dir)
    parser.add_argument('--prefix', type=str, help='String to replace with basepath found in imports', default=default_prefix)
    args = parser.parse_args()

    logging.getLogger(__name__).info("Converting " + args.file + " to TPTP format")
    ontology = Parser.parse_file(args.file, args.prefix, args.loc, args.noresolve)

    if (args.output==tptp_output):
        output = ontology.to_tptp(args.noresolve)
    elif (args.output==ladr_output):
        output = ontology.to_ladr(args.noresolve)

    # the following assumes that the names of the configuration sections are the same as the names of the output (tptp/ladr)
    if args.noresolve:
        ending = Filemgt.read_config(args.output, 'all_ending')
    else:
        ending = ""

    ending = ending + Filemgt.read_config(args.output, 'ending')

    print(ending)

    tptp_file_name = Filemgt.get_full_path(os.path.normpath(os.path.join(args.loc, args.file)),
                                           folder=Filemgt.read_config('tptp','folder'),
                                           ending=ending)
    #ontology.get_all_modules()

    with open(tptp_file_name, "w") as f:
        for sentence in output:
            print(sentence)
            f.write(sentence + "\n")
        f.close()

