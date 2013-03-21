'''
Created on 2013-03-19

@author: Torsten Hahmann
'''

import sys
from ClifModuleSet import ClifModuleSet

if __name__ == '__main__':
    import sys
    # global variables
    options = sys.argv
    m = ClifModuleSet(options[1])
    print str(m.get_imports())
    #m.run_full_consistency_check()
    m.run_consistency_check_by_subset()
