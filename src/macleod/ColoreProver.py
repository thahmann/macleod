'''
Created on 2010-11-05

@author: torsten
'''

from .VAMPIRE import VAMPIRE
from .ClifModule import ClifModule
import atexit, os, datetime, filemgt, process, ladr
import sys

#from PredicateOrderHeuristic import *
#from PredicateWeightHeuristic import *

class ColoreProver(object):

    # logical connectives in CLIF
    clif_logical_connectives = ['not', 'and', 'or', 'iff', 'if', 'exists', 'forall']
    # CLIF symbols that are logically irrelevant
    irrelevant_clif_symbols = ['cl-text', 'cl-module', 'cl-imports']
    # CLIF quantifiers
    quantifiers = ['forall', 'exists']

    # names of the provers and modelfinders used
    provers = {}
    finders = {}


    # initialize with a set of files to be processed (for lemmas)
    def __init__(self, processing=None):

        self.clif = True
        self.run_prover = True
        self.test_heuristics = False
        self.tidy = False
        self.p9_file_name = ''
        self.tptp_file_name = ''

        # list of clif files still to process
        self.processing = []
        # list of already processes clif imports (list of ClifModule)
        self.imports = []
        # list of nonlogical symbols that occur in any imported files
        # it is a tuple [symbol, count, d_min, d_max] where
        # symbol: name of the symbol
        # count: total number of Occurrences
        # d_min: minimal depth in the CL-import tree where it occurs
        # d_max: maximal depth in the CL-import tree where it occurs
        self.nonlogical_symbols = []
        # the primitive and potentially some defined predicates occurring in any imported files
        self.primitive_predicates = []
        # a list of predicates that are definitively defined predicates occurring in any imported files
        self.defined_predicates = []
        # the functions occurring in any imported files
        self.nonskolem_functions = []
        # list of special symbols that will be replaced in the p9 and the tptp translation
        self.special_symbols = []

        if processing:
            self.processing = processing

    # initially set the name of the top module
    # NOT to be used later on
    def set_module_name(self,module_name):  
        self.processing.append((module_name, 0))

    def get_module_name(self):
        if len(self.imports)>0:
            return self.imports[0].module_name


    # process the processing list until it is empty
    def prepare(self):
        while self.processing:
            (module, depth) = self.processing[0]
            #print 'processing list:'
            #print self.processing
            m = ClifModule(self, module, depth)
            self.processing.remove((module, depth))
            self.imports.append(m)
            #print '--- p9_files ---'
            #print p9_files    
        atexit.register(self.cleanup)


    # add a module to the processing list if it hasn't been included before
    def append_module(self,new_module_name, depth):
        existing = False
        # self.processing is a list of names
        for (p, _) in self.processing:
            if new_module_name == p:
                existing=True
                break
        # self.imports is a list of ClifModules
        for p in self.imports:
            if new_module_name == p.module_name:
                existing=True
                break 
        if not existing:
            print('|-- imports: ' + new_module_name + ' (depth ' + str(depth) + ')')
            # This is the only place where we increase the depth!!
            self.processing.append((new_module_name, depth))

    # add the nonlogical symbols from a processed clif module
    def append_nonlogical_symbols(self,new_nonlogical_symbols,depth):
        for symbol in new_nonlogical_symbols:
            found = False
            for (entity, count, d_min, d_max) in self.nonlogical_symbols:
                if symbol == entity:
                    # already in named entities, we just update the count and the depth:
                    # we want to keep track of two kinds of depths: the minimal and the maximal
                    # the new max. depth is the furthest away from the actual module_name as possible
                    found = True
                    index = self.nonlogical_symbols.index([symbol, count, d_min, d_max])
                    self.nonlogical_symbols[index]=[symbol, count+1, d_min, depth]
                    break;
                else:
                    continue
            if not found:
                #print 'found ' + words[0] + ' in line: ' + line
                #a NEW meaningful named entity has been found
                self.nonlogical_symbols.append([symbol, 1, depth, depth])


    # extract the predicates and functions from prover9 mock run
    def extract_p9_predicates_and_functions (self):

        #print 'extract predicates and functions'
        prover9args = 'prover9 -t 0 -f '


        for f in self.imports:
            prover9args += f.p9_file_name + ' '

        options_file = ladr.get_p9_optionsfile(self.get_module_name(), verbose=False)
        prover9args += ' ' + options_file + ' '


        # would be better to create a temporary single_file or read the output stream directly
        temp_file = self.get_module_name() + '_order' + filemgt.read_config('ladr','ending')
        prover9args += ' > ' + temp_file
        print(prover9args)
        process.createSubprocess(prover9args)
        p9.wait()

        order_file = open(temp_file, 'r')
        line = order_file.readline()
        predicates = None
        functions = None
        while line:
            if line.find('predicate_order') > -1:
                predicateline = line[line.find('predicate_order([')+len('predicate_order([')+1:-4]
                predicates = predicateline.split()
                for i in range(len(predicates)):
                    predicates[i] = predicates[i].replace(',','')
                line = order_file.readline()
                functionline = line[line.find('function_order([')+len('function_order([')+1:-4]
                functions = functionline.split()
                for i in range(len(functions)):
                    functions[i] = functions[i].replace(',','')
                break
            line = order_file.readline()

        order_file.close()
        #print 'temp single_file : ' + temp_file
        #print 'options single_file : ' + options_file
        os.remove(temp_file)
        os.remove(options_file)
        if predicates and functions:
            return (predicates, functions)
        else:
            return ([], [])

    # extracts the predicates and functions from the output of a prover9 mock run
    def get_predicates_and_functions (self):

        # process the predicates and functions
        predicates = []
        functions = [] 

        (predicates, functions) = self.extract_p9_predicates_and_functions()

        #print 'all predicates: ' + str(predicates)
        #print 'all functions: ' + str(functions)
        #print 'all named entities: ' + str(namedentities)

        # extracting defined predicates, (potentially) primitive predicates, and functions   
        for function in functions:
            for (entity, count, depth_min, depth_max) in self.nonlogical_symbols:
                if function == entity:
                    self.nonskolem_functions.append([entity, count, depth_min, depth_max])

        for (predicate, count, depth_min, depth_max) in self.nonlogical_symbols:
            if predicate in predicates:
                self.primitive_predicates.append([predicate, count, depth_min, depth_max])
            else:
                if predicate not in functions:
                    self.defined_predicates.append([predicate, count, depth_min, depth_max])

        print('all primitive predicates: ' + str(self.primitive_predicates))
        print('all defined predicates: ' + str(self.defined_predicates))
        print('all functions: ' + str(self.nonskolem_functions))


    def select_systems (self, outfile_stem):
        """read the activated provers and model finders from the configuration single_file
        return values:
        provers_dict -- a dictionary of all provers to be used with commands as keys and a set of return values as value
        finders_dict -- a dictionary of all model finders to be used with commands as keys and a set of return values as value
        """
        provers_dict = {}
        finders_dict = {}

        provers = filemgt.read_config('active','provers').split(',')
        finders = filemgt.read_config('active','modelfinders').split(',')

        provers = [ s.strip() for s in provers ]
        finders = [ s.strip() for s in finders ]

        for prover in provers:
            codes = self.get_posititve_returncodes(prover)
            cmd = ladr.get_system_command(prover, self.imports, outfile_stem)
            provers_dict[cmd] = codes
            self.provers[prover] = cmd
        for finder in finders:
            codes = self.get_posititve_returncodes(finder)
            cmd = ladr.get_system_command(finder, self.imports, outfile_stem)
            finders_dict[cmd] = codes
            self.finders[finder] = cmd

        return (provers_dict, finders_dict)


    def get_posititve_returncodes(self,name):
        return self.get_returncodes(name)

    def get_unknown_returncodes(self,name):
        return self.get_returncodes(name, type="unknown_returncode")

    def get_returncodes(self,name,type="positive_returncode"):
        codes = filemgt.read_config(name,type).split(',')
        codes = [ int(s.strip()) for s in codes ]
        return codes


    def consolidate_results(self, provers_rc, finders_rc):
        """ check all the return codes from the provers and model finders to find whether a model or inconsistency has been found
        return values:
        consistent (-1) -- an inconsistency has been found in the ontology
        unknown (0) -- unknown result (no model and no inconsistency found)
        inconsistent (1) -- model found, the ontology is consistent
         """
        return_value = 0

        for finder in list(self.finders.keys()):
            rc = finders_rc[self.finders[finder]]
            if rc in self.get_posititve_returncodes(finder):
                return_value = 1
            elif rc not in self.get_unknown_returncodes(finder):
                print(finder + ' returned with unknown error code ' + str(rc))
        for prover in list(self.provers.keys()):
            rc = provers_rc[self.provers[prover]]
            if rc in self.get_posititve_returncodes(prover):
                if not return_value==1:
                    return_value = -1
                else:
                    return_value == -100 
            elif rc not in self.get_unknown_returncodes(prover):
                print(prover + ' returned with unknown error code ' + str(rc))

        if return_value==-1: return "inconsistent"
        elif return_value==1: return "consistent"
        elif return_value==0: return "unknown"
        else: return "contradiction"


    def run_consistency_check(self, options_files = None):
        """ test the input for consistency by trying to find a model or an inconsistency"""
        if self.run_prover:    
            # want to create a subfolder for the output files
            outfile_stem = filemgt.get_name_with_subfolder(self.imports[0].module_name, 
                                                            filemgt.read_config('output','folder')) 

            (provers, finders) = self.select_systems(outfile_stem)

            # run provers and modelfinders simultaneously and wait until one returns
            (prc, frc) = process.raceProcesses(provers, finders)

            print(self.consolidate_results(provers, finders))


    # find minimum necessary axiom sets
    def find_axiom_subset_necessary_for_proof (self, lemma_names, lemma_files, output_file_infix = ''):

        return
        # simple algorithm: check whether we can construct a counterexample using a smaller set
        # of so, increase the set

        # first need to construct a dependency graph during initial clif importing
        # TODO 


    # get a list of all p9files created here
    def get_p9_files(self):
        p9_files = []
        for m in self.imports:
            p9_files.append(m.p9_file_name)
        return p9_files


    # translate the module and all imported modules (Common Logic files) to a single TPTP single_file
    def get_single_tptp_file (self, number=0):

        single_p9_file = ladr.get_single_p9_file(get_module_name)
        ending = ''
        if not number==0:
            ending = '_' + str(number)

        self.tptp_file_name = filemgt.get_name_with_subfolder(self.imports[0].module_name,
                                                              filemgt.read_config('tptp','folder'),
                                                              ending + filemgt.read_config('tptp','all_ending'))

        TPTP.ladr_to_tptp(self.p9_file_name, self.tptp_file_name)


    # try to prove all lemmas with vampire
    def run_lemmas_with_vampire(self, lemma_name, number, use_previous=False):

        self.get_single_tptp_file()

        nonlogical_symbols = self.nonlogical_symbols
        for symbol in nonlogical_symbols:
            for special in self.special_symbols:
                if symbol[0]==special[0]:
                    symbol[0]= special[1]

        #print self.nonlogical_symbols+self.special_symbols+'\n'

        vampire = VAMPIRE()
        for i in range(1, number+1):
            self.get_single_tptp_file(i)
            vampire.lowercase_tptp_file(self.tptp_file_name, self.nonlogical_symbols+self.special_symbols)
            vampire.select_lemma(self.tptp_file_name,i, number+1, use_previous)

            print('--------------------------------------') 
            print('Trying to prove ' + self.tptp_file_name)  
            print('--------------------------------------') 

            vampire_lemma_file_name = filemgt.get_name_with_subfolder(lemma_name, 
                                                                      read_config('output','folder'), 
                                                                      '_' + str(i)+ read_config('vampire','ending'),)
            # vampire command (appending to output single_file)
            vampire_cmd = vampire.get_vampire_basic_cmd(self.tptp_file_name) + ' >> ' + vampire_lemma_file_name
            print(vampire_cmd)

            # edit vampire_lemma_file to include basic information about execution data, time and command 
            single_file =  open(vampire_lemma_file_name, 'w')
            single_file.write('============================= Vampire ================================\n')
            single_file.write(vampire.get_version()+'\n')
            now = datetime.datetime.now()
            single_file.write(now.strftime("%a %b %d %H:%M:%S %Y")+'\n')
            single_file.write('The command was \"' + vampire_cmd + '\"\n')
            single_file.write('============================== end of head ===========================\n')
            single_file.close()

            vampire.run_vampire(vampire_cmd)


    # attempt to prove a single sentence from the axioms 
    def run_lemma(self, lemma_name, lemma_file, output_file_infix =''):

        p9_lemma_file_name = filemgt.get_name_with_subfolder(lemma_name, 
                                                            read_config('output','folder'), 
                                                            output_file_infix + read_config('prover9','ending'))
        p9cmd = ladr.get_p9_cmd(self.imports) + lemma_file + ' > ' + p9_lemma_file_name
        print(p9cmd)

        m4_lemma_file_name = filemgt.get_name_with_subfolder(lemma_name, 
                                                            read_config('output','folder'), 
                                                            output_file_infix + read_config('mace4','ending'))
        m4cmd = ladr.get_m4_cmd(self.imports) + lemma_file + ' > ' + m4_lemma_file_name
        print(m4cmd)

        # run both prover9 and mace4 simultaneously and wait until one returns
        provers = {p9cmd: {0,101,102}}
        finders = {m4cmd: {0,3,4,101,102}}

        # run both prover9 and mace4 simultaneously and wait until one returns
        (prc, frc) = process.raceProcesses(provers, finders)

        if frc['mace4'] == 0:
            print('Counterexample found')
            return False
        elif prc['prover9'] == 0:
            print('Lemma proved')
            return True
        elif frc['mace4'] == 2:
            print('Mace unable to find a counterexample in the given range of domain sizes')
            return None
        elif prc['prover9'] == 2:
            print('Prover9 unable to construct a proof')
            return None
        else:
            print('result unknown; returncodes (mace4, prover9): ')
            print(frc['mace4'])
            print(prc['prover9'])
            return None

    def write_lemma_summary(self, lemma_results):
        #TODO
        return



#    def check_consistency(self):
#        (predicates_primitive, self.predicates_defined, self.functions_nonskolem) = self.get_predicates_and_functions(p9_files, namedentities)
#        if not self.test_heuristics:
#            # single run
#            #weights = PredicateWeightHeuristic.predicate_weight_heuristic_occurence_count(predicates_primitive, [])
#            #weights_file = PredicateWeightHeuristic.create_predicate_weight_file(imported[0][0] + '.weights', weights)
#            self.weights_file = None
#            if self.run_prover:
#                #run_consistency_checks(imported[0][0] + '_oc' , p9_files, [options_file, weights_file])
#                self.run_consistency_checks(self.imports[0], self.get_p9_files()) 
#        else:
#            # testing with multiple heuristics
#            orders = HeuristicTestSet.get_all_tests(self.imported[0][0], predicates_primitive, None)
#            if self.run_prover:
#                print ' ---- EXPERIMENTS ---- '
#                for order in orders:
#                    print '----------------------' 
#                    print '--- TESTCASE: ' + order[0] + ' ---' 
#                    print '----------------------' 
#                    self.run_consistency_checks(self.imported[0][0] + '_' + order[0], p9_files, [options_file, order[1]])


    # delete unnecessary files at the end
    def cleanup(self):
        if self.tidy:          
            LADR.cleanup_option_files()  
            for m in self.imports:
                if os.path.exists(m.p9_intermediary_file_name):
                    os.remove(m.p9_intermediary_file_name)
                if os.path.exists(m.clif_processed_file_name):
                    os.remove(m.clif_processed_file_name)


    def print_help(self):
        print('Ontology tool suite for ontology verification in COLORE:')
        print('Copyright 2010-2012: Torsten Hahmann')
        print('----------')
        print('----------')
        print('')
        print('USAGE 1: ColoreProver clif-single_file [-l] [-t] [-noclif] [-norun] [-tidy]')
        print('----------')
        print('-l         prove a set of lemmas')
        print('-o         use a predicate ordering heuristic (currently only in combination with -l')
        print('-t         run a complex test suite (compare several heuristics) on the input')
        print('-noclif    skip the clif translation, start with the given p9 files instead')
        print('-norun     skip any proofs or consistency checks (mainly for generating/updating prover9 files)')
        print('-tidy      delete all intermediary files upon completion')
        print('ANY COMBINATIONS OF THE ABOVE ARE ALLOWED')
        print('----------')
        print('----------')
        print('')
        print('USAGE 2: ColoreProver clif-single_file -tptp [-s]* [-tidy]')
        print('----------')
        print('            translates theory to tptp syntax')
        print('-s=replacedSymbol:replacementSymbol')
        print('           In the tptp translation, replace all occurrences of replacedSymbol by replacementSymbol.')
        print('           The replacedSymbol can be single-quoted.')  
        print('----------')
        print('----------')
        print('')
        print('USAGE 3: ColoreProver clif-single_file -vam [-s]* [-vamlemmas] [-tidy]')
        print('----------')
        print('            attempts a proof with Vampire')
        print('-s=replacedSymbol:replacementSymbol')
        print('           In the tptp translation, replace all occurrences of replacedSymbol by replacementSymbol.')
        print('           The replacedSymbol can be single-quoted.')  
        print('-vamlemmas reuse previous lemmas (as specified by the order in the single_file)')
        print('----------')
        print('----------')
        print('')
        print('USAGE 4: ColoreProver clif-source-axiomatization clif-goal-axiomaization -int [-s]* [-tidy]')
        print('----------')
        print('            proves a relative interpretation using the sentences in clif-source-axiomatization as axioms')
        print('            and trying to prove each sentence in clif-goal-axiomaization individually.')
        print('            The source axiomatization must inlcude the mapping axioms.')
        print('-s=replacedSymbol:replacementSymbol')
        print('           In the tptp translation, replace all occurrences of replacedSymbol by replacementSymbol.')
        print('           The replacedSymbol can be single-quoted.')  
        print('----------')
        print('----------')
        print('')

# run program
if __name__ == '__main__':

    cp = ColoreProver()

    # global variables
    options = sys.argv
    del options[0]

    if not options:
        cp.print_help()
        sys.exit()

    if '-h' in options:
        options.remove('-h')
        cp.print_help()
        sys.exit()

    if '-noclif' in options:
        options.remove('-noclif')
        cp.clif = False

    # read command-line argument '-t' to check whether a test suite containing several heuristics is started
    if '-t' in options:
        options.remove('-t')
        cp.test_heuristics = True

    if '-norun' in options:
        options.remove('-norun')
        cp.run = False

    if '-tidy' in options:
        options.remove('-tidy')
        cp.tidy = True



    # read command-line argument '-l' to check whether a set of lemmas is to be proven
    if '-l' in options:
        options.remove('-l')

        if len(options)>0:
            source_name = options[0]
            del options[0]
            cp.set_module_name(source_name)
            # create a second instance of the ColoreProver to check consistency first
            cp_con = ColoreProver()
            cp_con.set_module_name(source_name)
            cp_con.prepare()
            cp_con.run_consistency_check()
        else:
            cp.print_help()

        (module, depth) = cp.processing[0]
        m = ClifModule(cp, module, depth)
        cp.processing.remove((module, depth))
        cp.imports.append(m)

        LADR.get_single_p9_file(cp.get_module_name())

        (sentences_names, sentences_files) = ladr.get_individual_p9_sentences(cp.imports[0].module_name,cp.p9_file_name)

        print(cp.processing)

        axiom_cp = ColoreProver(cp.processing)
        axiom_cp.prepare()
        axiom_cp.tidy = cp.tidy

        lemma_results = []

        # use a predicate ordering heuristic (relevance1 by default)
        if '-o' in options:   
            infix = '_relevance1'
            from PredicateOrderHeuristic import PredicateOrderHeuristic
            axiom_cp.get_predicates_and_functions()
            poh = PredicateOrderHeuristic(axiom_cp.cfm)
            order = poh.predicate_order_heuristic_relevance1(axiom_cp.primitive_predicates + axiom_cp.defined_predicates, [])
            #print 'order:'
            #print order
            order_file = poh.create_predicate_order_file(axiom_cp.get_module_name() + infix, order) 


        for i in range(len(sentences_files)):
            print('--------------------------------------') 
            print('Trying to prove ' + str(sentences_files[i])) 

            # single run
            if cp.run_prover:
                # test output of all non-logical symbols
                #print axiom_cp.nonlogical_symbols

                ##order = predicate_order_heuristic_first_occurence(predicates_primitive, predicates_lemma)
                if '-o' in options:    
                    LADR.get_p9_optionsfile(sentences_files[i], verbose=False)
                    lemma_results.append(axiom_cp.run_lemma(sentences_names[i], sentences_files[i], infix))
                else:
                    lemma_results.append(axiom_cp.run_lemma(sentences_names[i], sentences_files[i]))
                LADR.cleanup_option_files()

        # print summary
        print('--------------------------------------') 
        print('--------------------------------------') 
        for i in range(len(lemma_results)):
            print('Lemma ' + str(i+1) + ': ' + str(lemma_results[i]))
        print('--------------------------------------') 
        print('--------------------------------------') 



    elif '-int' in options:
        options.remove('-int')
        if len(options)>0:
            source_name = options[0]
            del options[0]
            cp.set_module_name(source_name)
            cp.prepare()
        else:
            cp.print_help()
            sys.exit()

    # TODO interpretation  
        print('--------------------------------------') 
        print('   Proving relative interpretation') 
        print('--------------------------------------') 
        target_name = options[0]
        del options[0]
        target_cp = ColoreProver()
        target_cp.set_module_name(target_name)
        target_cp.tidy = cp.tidy
        target_cp.prepare()

        # rename symbols in the target axiomatization as instructed
        if options and len(options)>0:        
            for o in options:
                key = o.split('=')
                if key[0]=='-s':
                    key[1]= o[3:]
                    print('Found special symbol: ' + key[1])
                    value = key[1].replace('\'','').split(":")
                    target_cp.special_symbols.append((value[0],value[1]))

        # construct a single p9 files from the target axiomatization
        LADR.get_single_p9_file(target_cp.get_module_name())

        # TODO: this may not work correctly (wrong number of lemmas to prove)
        (sentences_names, sentences_files) = ladr.get_individual_p9_sentences(target_name,target_cp.p9_file_name)

        for i in range(len(sentences_files)):
            print('--------------------------------------') 
            print('Trying to prove ' + sentences_files[i])  
            print('--------------------------------------') 

            # single run
            if cp.run_prover:
                cp.ladr.options_files.append(cp.cfm.get_p9_optionsfile(sentences_files[i], verbose=False))
                cp.run_lemma(sentences_names[i], sentences_files[i])
                cp.ladr.options_files = []


    # translate to tptp
    elif '-tptp' in options:
        options.remove('-tptp')
        source_name = options[0]
        del options[0]
        cp.set_module_name(source_name)
        cp.prepare()

        # get symbol replacement for translation to tptp (all must be lower case, no special characters) 
        for o in options:
            key = o.split('=')
            if key[0]=='-s':
                key[1]= o[3:]
                print('Found special symbol: ' + key[1])
                value = key[1].replace('\'','').split(":")
                cp.special_symbols.append((value[0],value[1]))

        cp.get_single_tptp_file()

    # run a proof with vampire
    elif '-vam' in options:
        source_name = options[0]
        del options[0]
        cp.set_module_name(source_name)

        (module, depth) = cp.processing[0]
        m = ClifModule(cp, module, depth)
        cp.processing.remove((module, depth))
        cp.imports.append(m)

        LADR.get_single_p9_file(cp.get_module_name())

        (sentences_names, sentences_files) = ladr.get_individual_p9_sentences(cp.imports[0].module_name,cp.p9_file_name)

        #print len(sentences_names)

        cp.prepare()

        # get symbol replacement for translation to tptp (all must be lower case, no special characters) 
        for o in options:
            key = o.split('=')
            if key[0]=='-s':
                key[1]= o[3:]
                print('Found special symbol: ' + key[1])
                value = key[1].replace('\'','').split(":")
                cp.special_symbols.append((value[0],value[1]))

        if '-vamlemmas' in options:
            cp.run_lemmas_with_vampire(source_name, len(sentences_names), True)
        else:
            cp.run_lemmas_with_vampire(source_name, len(sentences_names))


    # run consistency check
    else:
        source_name = options[0]
        cp.set_module_name(source_name)
        cp.prepare()
        cp.run_consistency_check()


# END of run program    

