'''
Created on 2013-07-22

@author: Torsten Hahmann
'''

import macleod.Filemgt as filemgt
import macleod.Clif as clif
from macleod.ClifModuleSet import ClifModuleSet
from bin import licence, check_consistency
import datetime
import sys


def nontrivially_consistent(filename, m, options=[]):
    (consistent, m) = check_consistency.consistent(filename, m, options)

    if consistent==None or consistent==True:  # no need to check nontrivial consistency if it is not consistent at all      
        #m = ClifModuleSet(filename)
        definitional_modules = []
        if "-simple" in options:
            i = m.get_top_module()
            if "-defs" not in options or i.is_simple_definition():
                definitional_modules.append(i)
        else:
            for i in m.get_imports():
                if "-defs" not in options or i.is_simple_definition():
                    definitional_modules.append(i)

        weak = "strong"
        defs = ""
        if "-weak" in options:
            weak = "weak"
        if "-defs" in options:
            defs = "definitional "
        print("\n+++++++++++++++++++++\nProving "+weak +" nontrivial consistency for all " + str(len(definitional_modules))  + " " + defs + "modules of "+ m.get_module_name() +":\n+++++++++++++++++++++")
        for n in definitional_modules:
            print(n.module_name)
        print("+++++++++++++++++++++\n")

        if len(definitional_modules)==0:
            print("NO DEFINITIONS FOUND TO CHECK NONTRIVIAL CONSISTENCY FOR.")

        for i in definitional_modules:
            if "-defs" not in options or i.is_simple_definition():
                if "-defs" in options:
                    if "-all" in options:
                        defined_symbols = m.get_defined_nonlogical_symbols()
                    else:
                        defined_symbols = i.get_defined_symbols()
                else: # not just definitions
                    if "-all" in options:
                        defined_symbols = m.get_nonlogical_symbols()
                    else:
                        defined_symbols = i.get_nonlogical_symbols()

                symbol_string = ""
                for (symbol, arity) in defined_symbols:
                    symbol_string += symbol + '('+ str(arity) + ') '

                print("\n+++++++++++++++++++++\nProving "+weak +" nontrivial consistency of nonlogical symbols " + symbol_string + " in module " + i.module_name + "\n+++++++++++++++++++++\n")

                #for (symbol, arity) in defined_symbols:
                    #print "Symbol " + str(symbol) + " has arity " + str(arity)

                # need to create new CL file that imports the definition module and adds a sentence stating that n distinct elements in this relation exist

                module_name_modifier = "" 
                if "-all" in options:
                    module_name_modifier += "_all"
                if "-weak" in options:
                    module_name_modifier += "_weak"
                (module_name, path) = filemgt.get_path_with_ending_for_nontrivial_consistency_checks(i.module_name+module_name_modifier)

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
                    if arity>0:
                        if "-weak" in options: # weak nontrivial consistency: each entity is independent from all others
                            for n in range(arity):                            
                                clif_file.write(construct_existential_sentence(symbol, arity, negation=False, all_distinct=False, position=n) + '\n\n')
                                clif_file.write(construct_existential_sentence(symbol, arity, negation=True, all_distinct=False, position=n) + '\n\n')

                        else: # strong nontrivial consistency: all participating entities have to be disjoint
                            clif_file.write(construct_existential_sentence(symbol, arity, negation=False, all_distinct=True) + '\n\n')
                            clif_file.write(construct_existential_sentence(symbol, arity, negation=True, all_distinct=True) + '\n\n')

                clif_file.write(')\n') # closing "cl-module"

                clif_file.close()

                m2 = ClifModuleSet(path)
                check_consistency.consistent(path, m2, options=options)            


def construct_existential_sentence (symbol, arity, negation=False, all_distinct=True, position=0):

    def construct_pairwise_distinct_term (symbol, arity, position):
        term = ""
        for i in range(arity):
            if i!=position: # add distinct from all others condition 
                term += '    (not (= X' + str(position) + ' X' + str(i) + '))\n'  
        return term


    def construct_all_distinct_term (symbol, arity):
        term = ""
        for i in range(arity-1):  # add pairwise distinct conditions
            for j in range(i+1, arity):
                term += '    (not (= X' + str(i) + ' X' + str(j) + '))\n'
        return term  


    existential_sentence = '(' + clif.CLIF_EXISTENTIAL + ' ('
    for i in range(arity):
        existential_sentence += 'X' + str(i) + ' '
    existential_sentence = existential_sentence[:-1] + ')\n  (and\n' # remove last space which is unnecessary
    if negation:
        existential_sentence += '  (not\n' 
    existential_sentence += '    (' + symbol
    for i in range(arity):
        existential_sentence += ' X' + str(i)
    existential_sentence += ')\n'
    if negation:
        existential_sentence += '  )\n'

    if all_distinct:
        existential_sentence += construct_all_distinct_term(symbol, arity)
    else: 
        existential_sentence += construct_pairwise_distinct_term(symbol, arity, position)

    existential_sentence += '  )\n' # closing "and"
    existential_sentence += ')\n' # closing "existential"
    return existential_sentence





def print_options ():
    print("USAGE: check_nontrivial_consistency file [options]")
    print("with the following options:")
    print("-simple: check only consistency of the entire ontology and nontrivial consistency of the top definitions, assuming that file contains definitions.")
    print("-weak: for the nontrivial consistency check only ensure that every pair of parameters can have distinct values. Otherwise, the values of all parameters must be allowed to be distinct.")
    print("-all: check for all symbols in module(s).")
    print("-defs: check only for defined symbols.")


if __name__ == '__main__':
    licence.print_terms()
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    if not options:
        print_options()
        sys.exit()
    filename = options.pop()

    m = ClifModuleSet(filename)
    nontrivially_consistent(filename, m, options)
