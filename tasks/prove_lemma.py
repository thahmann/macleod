'''
Created on 2013-03-29

@author: Torsten Hahmann
'''

from tasks import *
import sys
from src import *
from src.ClifModuleSet import *
from prove_lemma import *


def run_simple_check(m):
    (i, r) = m.run_simple_consistency_check().popitem()
    if r==ClifModuleSet.PROOF:
        logging.getLogger(__name__).info("+++ LEMMA PROVED " +m.get_lemma_module().get_simple_module_name() + " from AXIOMS: " + str(m.get_axioms())  +"\n")
    elif r==ClifModuleSet.COUNTEREXAMPLE:
        logging.getLogger(__name__).info("+++ SENTENCE REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
    else:
        logging.getLogger(__name__).info("+++ SENTENCE NEITHER PROVED NOR REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
    
            
def prove (lemmas_filename, axioms_filename=None, options=[]):
        
    if axioms_filename is None:
        m = ClifModuleSet(lemmas_filename)
        #print "REMOVING " + m.get_top_module().module_name
        m.remove_module(m.get_top_module())
    else:
        m = ClifModuleSet(axioms_filename)
        
    lemmas = ClifLemmaSet(lemmas_filename)

    lemma_modules = lemmas.get_lemmas()
    for l in lemma_modules:
        logging.getLogger(__name__).debug("LEMMA MODULE: " + l.module_name + " TPTP_SENTENCE " + l.tptp_sentence +"\n")

    for l in lemma_modules:
        m.add_lemma_module(l)
        
        #print str(m.get_imports())
        
        if '-module' in options:
            results = m.run_consistency_check_by_subset(abort_signal = ClifModuleSet.PROOF, increasing=True)
            proved = False
            for (i, r) in results.iteritems():
                if r==ClifModuleSet.PROOF:
                    proved = True
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if not proved:
                run_simple_check(m)
                
        elif '-depth' in options:
            results = m.run_consistency_check_by_depth(abort_signal = ClifModuleSet.PROOF, increasing=True)
            proved = False
            for (i, r) in results.iteritems():
                if r==ClifModuleSet.PROOF:
                    proved = True
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if not proved:
                run_simple_check(m)
        
        elif '-simple' in options:
            run_simple_check(m)
        else:
            results = m.run_full_consistency_check()
            for (i, r) in results.iteritems():
                if len(results)==1 and r==ClifModuleSet.COUNTEREXAMPLE:
                    logging.getLogger(__name__).info("+++ SENTENCE REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
                if r==ClifModuleSet.PROOF:
                    proved = True
                    logging.getLogger(__name__).info("+++ LEMMA PROVED " +l.get_simple_module_name() + "from AXIOMS: " + str(i)  +"\n")
            if not proved:
                logging.getLogger(__name__).info("+++ SENTENCE NEITHER PROVED NOR REFUTED " +m.get_lemma_module().get_simple_module_name() + " in AXIOMS: " + str(m.get_axioms())  +"\n")
    

if __name__ == '__main__':
    # global variables
    licence.print_terms()
    options = sys.argv
    options.reverse()
    options.pop()
    if '-find' in options:
        options.remove('-find')
        axioms_filename = None
        lemmas_filename = options.pop()        
    else:
        axioms_filename = options.pop()
        lemmas_filename = options.pop()
    prove (lemmas_filename, axioms_filename=axioms_filename, options=options)
    
