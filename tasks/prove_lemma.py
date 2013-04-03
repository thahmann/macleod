'''
Created on 2013-03-29

@author: Torsten Hahmann
'''

import sys
from src import *
from src.ClifModuleSet import *

if __name__ == '__main__':
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    m = ClifModuleSet(options.pop())
    lemmas = ClifLemmaSet(options.pop())
    
    for l in lemmas.get_lemmas():
        m.add_lemma_module(l)
        m.get_single_tptp_file()
        
        if '-module' in options:
            results = m.run_consistency_check_by_subset(abort_signal = ClifModuleSet.PROOF, increasing=True)
            for (i, r) in results.iteritems():
                if r==ClifModuleSet.PROOF:
                    print l.get_simple_module_name() + " proved  by " + str(i) 
        elif '-depth' in options:
            m.run_consistency_check_by_depth()
        elif '-simple' in options:
            m.run_simple_consistency_check()
        else:
            m.run_full_consistency_check()
        