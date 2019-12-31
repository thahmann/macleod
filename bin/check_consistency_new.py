'''
Created on 2013-03-19

@author: Torsten Hahmann
'''
import os, sys, argparse, logging

sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")

from bin import licence
import macleod.Filemgt as Filemgt
import macleod.parsing.Parser as Parser
#from macleod.Filemgt import Filemgt

# defaults for the ontology directory and basepath
default_dir = Filemgt.read_config('system', 'path')
default_prefix = Filemgt.read_config('cl', 'prefix')

def consistent(filename, m, options=[]):  

    if '-module' in options:
        results = m.run_consistency_check_by_subset(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
    elif '-depth' in options:
        results = m.run_consistency_check_by_depth(abort=True, abort_signal=ClifModuleSet.CONSISTENT)
    elif '-simple' in options:
        results = m.run_simple_consistency_check()
    else:
        results = m.run_full_consistency_check(abort=True, abort_signal=ClifModuleSet.CONSISTENT)

    if len(results)==0:
        logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO MODULES FOUND IN " +str(m.get_imports()) +"\n")
    else:
        for (r, value, _) in results:
            if value==-1:
                logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: INCONSISTENCY FOUND IN " +str(r) +"\n")
                return (False, m)
        result_sets = [r[0] for r in results]
        result_sets.sort(key=lambda x: len(x))
        #print result_sets[0]
        #print results
        #print "+++++" + str(value)
        if results[0][1]==1:
            logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF " +str(result_sets[0]) +"\n")
            return (True, m)
        else:
            logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO RESULT FOR CONSISTENCY OF " +str(result_sets[0]) +"\n")
            if len(result_sets)>1:
                for (r, value, _) in results:
                    if value==1:
                        logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF SUBONTOLOGY " +str(r[0]) +"\n")
    return (None, m)


if __name__ == '__main__':
    licence.print_terms()

    parser = argparse.ArgumentParser(description='Function to check the consistency of a Common Logic ontology.')
    parser.add_argument('-f', '--file', type=str, help='Clif file', required=True)
    parser.add_argument('-n', '--noresolve', action="store_false", help='Prevent from automatically resolving imports', default=True)
    parser.add_argument('--loc', type=str, help='Path to directory containing ontology files', default=default_dir)
    parser.add_argument('--prefix', type=str, help='String to replace with basepath found in imports', default=default_prefix)
    args = parser.parse_args()

    path = os.path.normpath(os.path.join(args.loc, args.file))

    ontology = Parser.parse_file(args.file, args.prefix, args.loc, args.noresolve)

    if not(os.path.isfile(path)):
        logging.getLogger(__name__).error("Attempted to check consistency of non-existent file: " + path)
    else:
        ontology.check_consistency(resolve=not(args.noresolve))


