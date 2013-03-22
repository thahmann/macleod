'''
Created on 2013-03-22

@author: Torsten Hahmann
'''

import sys
from src.ClifModuleSet import ClifModuleSet

if __name__ == '__main__':
    import sys
    # global variables
    options = sys.argv
    m = ClifModuleSet(options[1])
    output = m.get_single_ladr_file()
    #print str(output)
    #return output
    #m.run_full_consistency_check()
    #m.run_consistency_check_by_subset()
