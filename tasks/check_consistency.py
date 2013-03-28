'''
Created on 2013-03-19

@author: Torsten Hahmann
'''

import sys
from src import *

if __name__ == '__main__':
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    m = ClifModuleSet(options.pop())
       
    if '-module' in options:
        m.run_consistency_check_by_subset()
    elif '-depth' in options:
        m.run_consistency_check_by_depth()
    elif '-full' in options:
        m.run_full_consistency_check()
    else:
        m.run_simple_consistency_check()
        
    
    print str(m.get_imports())
    m.run_consistency_check_by_subset()
