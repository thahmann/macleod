'''
Created on 2013-03-28

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
    
    # global variables
    parser = argparse.ArgumentParser(description='Utility function to convert Common Logic Interchange Format (.clif) files to TPTP syntax.')
    parser.add_argument('-f', '--file', type=str, help='Path to Clif file to parse', required=True)
    parser.add_argument('--resolve', action="store_true", help='Automatically resolve imports', default=True)
    parser.add_argument('-b', '--dir', type=str, help='Path to directory containing ontology files', default=default_dir)
    parser.add_argument('-s', '--prefix', type=str, help='String to replace with basepath found in imports', default=default_prefix)
    args = parser.parse_args()

    logging.getLogger(__name__).info("Converting " + args.file + " to TPTP format")
    ontology = Parser.parse_file(args.file, args.prefix, args.dir, args.resolve)

    tptp_output = ontology.to_tptp()

    if args.resolve:
        ending = Filemgt.read_config('tptp', 'all_ending')
    else:
        ending = Filemgt.read_config('tptp', 'select_ending')

    ending = ending + Filemgt.read_config('tptp', 'ending')

    tptp_file_name = Filemgt.get_full_path(os.path.normpath(os.path.join(args.dir, args.file)),
                                           folder=Filemgt.read_config('tptp','folder'),
                                           ending=ending)
    #ontology.get_all_modules()

    with open(tptp_file_name, "w") as f:
        for sentence in tptp_output:
            print(sentence)
            f.write(sentence + "\n")
        f.close()

