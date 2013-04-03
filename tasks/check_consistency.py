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
        
    if -1 in results.values():
        for r in results:
            if results[r]==-1:
                logging.getLogger(__name__).info(str(r) + " is inconsistent")
    else:
        logging.getLogger(__name__).info(str(m.get_imports()) + " is consistent")
    
    #print str(m.get_imports())
    #m.run_consistency_check_by_subset()
