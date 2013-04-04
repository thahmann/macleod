'''
Created on 2013-03-19

@author: Torsten Hahmann
'''

import sys, logging
from src import *

if __name__ == '__main__':
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    m = ClifModuleSet(options.pop())
       
    if '-module' in options:
        results = m.run_consistency_check_by_subset(abort=True)
    elif '-depth' in options:
        results = m.run_consistency_check_by_depth(abort=True)
    elif '-simple' in options:
        results = m.run_simple_consistency_check()
    else:
        results = m.run_full_consistency_check(abort=True)
        
    if len(results)==0:
        logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO MODULES FOUND IN " +str(m.get_imports()) +"\n")        
    elif -1 in results.values():
        for (r, value) in results:
            if value==-1:
                logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: INCONSISTENCY FOUND IN " +str(r) +"\n")
    else:
        result_sets = results.keys()
        result_sets.sort(lambda x,y: cmp(len(x), len(y)))
#        print result_sets[0]
#        print results
#        print "+++++" + str(value)
        if results.get(result_sets[0])==1:
            logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF " +str(result_sets[0]) +"\n")
        else:
            logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: NO RESULT FOR CONSISTENCY OF " +str(r) +"\n")
            for (r, value) in result_sets:
                if value==1:
                    logging.getLogger(__name__).info("+++ CONSISTENCY CHECK TERMINATED: PROVED CONSISTENCY OF SUBONTOLOGY " +str(r) +"\n")
