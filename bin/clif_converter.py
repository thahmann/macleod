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

# defaults for the ontology directory and basepath
default_dir = Filemgt.read_config('system', 'path')
default_prefix = Filemgt.read_config('cl', 'prefix')
tptp_output = 'tptp'
ladr_output = 'ladr'


def convert_single(file, output, noresolve, loc, prefix):

    logging.getLogger(__name__).info("Converting " + args.file + " to " + output + " format")
    ontology = Parser.parse_file(file, prefix, loc, noresolve)

    if (output==tptp_output):
        results = ontology.to_tptp(noresolve)
    elif (output==ladr_output):
        results = ontology.to_ladr(noresolve)

    # the following assumes that the names of the configuration sections are the same as the names of the output (tptp/ladr)
    if noresolve:
        ending = Filemgt.read_config(output, 'all_ending')
    else:
        ending = ""

    ending = ending + Filemgt.read_config(output, 'ending')

    output_file_name = Filemgt.get_full_path(os.path.normpath(os.path.join(loc, file)),
                                           folder=Filemgt.read_config('tptp','folder'),
                                           ending=ending)
    #ontology.get_all_modules()

    with open(output_file_name, "w") as f:
        for sentence in results:
            print(sentence)
            f.write(sentence + "\n")
        f.close()



def convert_all(folder, output, noresolve, loc, prefix):

    tempfolder = Filemgt.read_config('converters', 'tempfolder')
    ignores = [tempfolder]
    cl_ending = Filemgt.read_config('cl', 'ending')
    logging.getLogger(__name__).info("Traversing folder " + folder)

    for directory, subdirs, files in os.walk(folder):
        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                if single_file.endswith(cl_ending):
                    file = os.path.join(directory, single_file)
                    logging.getLogger(__name__).info("Found CL file " + file)
                    convert_single(file, output, noresolve, loc, prefix)


if __name__ == '__main__':
    licence.print_terms()

    parser = argparse.ArgumentParser(description='Utility function to convert Common Logic Interchange Format (.clif) files to the TPTP or LADR syntax.')
    parser.add_argument('-f', '--file', type=str, help='Clif file or folder to parse', required=True)
    parser.add_argument('-o', '--output', type=str, help='Output format', default=tptp_output)
    parser.add_argument('-n', '--noresolve', action="store_false", help='Prevent from automatically resolving imports', default=True)
    parser.add_argument('--loc', type=str, help='Path to directory containing ontology files', default=default_dir)
    parser.add_argument('--prefix', type=str, help='String to replace with basepath found in imports', default=default_prefix)
    args = parser.parse_args()

    path = os.path.normpath(os.path.join(args.loc, args.file))

    if os.path.isfile(path):
        convert_single(args.file, args.output, args.noresolve, args.loc, args.prefix)
    elif os.path.isdir(path):
        convert_all(path, args.output, args.noresolve, args.loc, args.prefix)
    else:
        logging.getLogger(__name__).error("Attempted to parse non-existent file or directory: " + path)


