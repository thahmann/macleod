'''
Created on 2013-07-22

@author: Torsten Hahmann
'''

from src import filemgt, clif
from src.ClifModuleSet import ClifModuleSet
from tasks import licence, check_consistency
import datetime
import logging
import sys

    
def nontrivially_consistent(filename, options=[]):
    options.append("-simple")
    (consistent, m) = check_consistency.consistent(filename, options)
    
    if consistent==None or consistent==True:  # no need to check nontrivial consistency of it is not consistent at all      
        #m = ClifModuleSet(filename)
        definitional_modules = []
        for i in m.get_imports():
            if i.is_simple_definition():
                definitional_modules.append(i)
        
        weak = "strong"
        if "-weak" in options:
            weak = "weak"
        print "\n+++++++++++++++++++++\nProving "+weak +" nontrivial consistency for all " + str(len(definitional_modules))  + " definitional modules of "+ m.get_module_name() +":\n+++++++++++++++++++++"
        for n in definitional_modules:
            print n.module_name
        print "+++++++++++++++++++++\n"
        
        
        for i in definitional_modules:
            if i.is_simple_definition():
                defined_symbols = i.get_defined_symbols()

                symbol_string = ""
                for (symbol, arity) in defined_symbols:
                    symbol_string += symbol + '('+ str(arity) + ')'

                print "\n+++++++++++++++++++++\nProving "+weak +" nontrivial consistency of nonlogical symbols " + symbol_string + " in module " + i.module_name + "\n+++++++++++++++++++++\n"
                
                #for (symbol, arity) in defined_symbols:
                    #print "Symbol " + str(symbol) + " has arity " + str(arity)
                
                # need to create new CL file that imports the definition module and adds a sentence stating that n distinct elements in this relation exist

                if "-weak" in options:
                    (module_name, path) = filemgt.get_path_with_ending_for_nontrivial_consistency_checks(i.module_name+"_weak")
                else:
                    (module_name, path) = filemgt.get_path_with_ending_for_nontrivial_consistency_checks(i.module_name)

                now = datetime.datetime.now()
                
                clif_file = open(path, 'w')
                clif_file.write("/** AUTOMATICALLY CREATED BY MACLEOD ON " + now.strftime("%a %b %d %H:%M:%S %Y")+'**/\n\n')
                clif_file.write('(' + clif.CLIF_TEXT + ' ' + module_name + '\n\n')
                clif_file.write('(' + clif.CLIF_IMPORT + ' ' + i.module_name + filemgt.read_config('cl','ending') + ')\n\n')
                
                # constructing a sentence of the form:
                # (exists (x1 x2 ...)
                #    (and
                #        (SYMBOL x1 x2 ...)
                #        (not (= x1 x2))
                #        (not (= ...
                #  )  )
                #
                # The assumption here is that there must exist a possibility that all the participating elements are distinct. 
                # If this weren't the case, the n-ary predicate could be reduced to a (n-1)-ary predicate.  This may be overly simplistic, but works for most of the case.
                # In particular, it fails if a binary relation is strictly reflexive, i.e. holds only for individual elements.
                # For predicates with n>2 this should probably be relaxed to:
                # every pairwise position of elements can be distinct.   
                for (symbol, arity) in defined_symbols:
                    if "-weak" in options: # weak nontrivial consistency: each entity is independent from all others
                        for n in range(arity):                            
                            existential_sentence = '(' + clif.CLIF_EXISTENTIAL + ' ('
                            for i in range(arity):
                                existential_sentence += 'x' + str(i) + ' '
                            existential_sentence += ')\n  (and\n    (' + symbol
                            for i in range(arity):
                                existential_sentence += ' x' + str(i)
                            existential_sentence += ')\n'
                            for i in range(arity):
                                if i!=n:
                                    existential_sentence += '    (not (= x' + str(n) + ' x' + str(i) + '))\n'  
                            existential_sentence += '  )\n'
                            
                            clif_file.write(existential_sentence + ')\n\n')
                            
                    else: # strong nontrivial consistency: all participating entities have to be disjoint
                        existential_sentence = '(' + clif.CLIF_EXISTENTIAL + ' ('
                        for i in range(arity):
                            existential_sentence += 'x' + str(i) + ' '
                        existential_sentence += ')\n  (and\n    (' + symbol
                        for i in range(arity):
                            existential_sentence += ' x' + str(i)
                        existential_sentence += ')\n'
                        for i in range(arity-1):  # add pairwise disjoint conditions
                            for j in range(i+1, arity):
                                existential_sentence += '    (not (= x' + str(i) + ' x' + str(j) + '))\n'  
                        existential_sentence += '  )\n'
                    
                        clif_file.write(existential_sentence + ')\n\n')

                    clif_file.write(')\n')
                    
                clif_file.close()
    
                check_consistency.consistent(path,options)            
                

if __name__ == '__main__':
    licence.print_terms()
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    filename = options.pop()
    nontrivially_consistent(filename, options)
