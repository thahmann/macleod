'''
Created on 2013-03-19

@author: Torsten Hahmann
'''

import sys
from bin import *
from macleod.ClifModuleSet import ClifModuleSet

import logging

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
    #licence.print_terms()
    # global variables

    options = sys.argv
    options.reverse()
    options.pop()
    filename = options.pop()
    m = ClifModuleSet(filename)
    derp, clif = consistent(filename, m, options)

