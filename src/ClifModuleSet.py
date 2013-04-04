'''
Created on 2010-11-05
Regrouped all methods that pertain to an import hierarchy into the new module ClifModuleSet on 2013-03-15

@author: Torsten Hahmann
'''

import sys
from src import *
from src.ReasonerSet import * 
import os, datetime, logging
#import atexit


class ClifModuleSet(object):

    CONSISTENT = 1
    INCONSISTENT = -1
    PROOF = -1
    COUNTEREXAMPLE = 1
    UNKNOWN = 0
    CONTRADICTION = -100
    

    module_name = ''

    # list of ClifModules that are imported and have been processed already   
    imports = set([])
    
    # keeps track of the lemma that needs to be proved; this is None if no lemma needs to be proved 
    lemma_module = None
    
    # list of imports that still require processing
    unprocessed_imports = set([])

    # list of nonlogical symbols that occur in any imported files
    # it is a tuple [symbol, count, d_min, d_max] where
    # symbol: name of the symbol
    # count: total number of Occurrences
    # d_min: minimal depth in the CL-import tree where it occurs
    # d_max: maximal depth in the CL-import tree where it occurs
    nonlogical_symbols = set([])
    
    # the primitive and potentially some defined predicates occurring in any imported files
    primitive_predicates = set([])

    # a list of predicates that are definitively defined predicates occurring in any imported files
    defined_predicates = set([])
    
    # the functions occurring in any imported files
    nonskolem_functions = set([])
    
    p9_file_name = ''
    tptp_file_name = ''
    
    # initialize with a set of files to be processed (for lemmas)
    def __init__(self, name):
        
        filemgt.start_logging()
        
        logging.getLogger(__name__).info("Creating ClifModuleSet " + name)

        m = ClifModule(name,0)
        m.module_set = self
        self.imports.add(m)
        self.module_name=m.get_simple_module_name()

        self.unprocessed_imports = self.unprocessed_imports.union(m.get_imports())

        while len(self.unprocessed_imports)>0:
            m = ClifModule(self.unprocessed_imports.pop(),0)
            m.module_set = self
            # Link the module to all its parents
            for cm in self.imports:
                if m.get_simple_module_name() in cm.get_imports():
                    m.add_parent(cm.get_simple_module_name(),cm.get_depth())

            self.imports.add(m)

            # add all the names of imported modules that have not yet been processed
            new_imports = set(m.get_imports()) - set([i.get_simple_module_name() for i in self.imports])
            for i in new_imports:
                logging.getLogger(__name__).info('|-- imports: ' + m.get_simple_module_name(i) + ' (depth ' + str(m.get_depth()+1) + ')')
                            
            self.unprocessed_imports = self.unprocessed_imports.union(new_imports)
        
        self.pretty_print()

#        atexit.register(self.cleanup)
    
    def pretty_print (self):

        print "\n++++++++++++\nall modules of "+ self.module_name +":\n++++++++++++"

        imports = self.get_sorted_imports()

        for n in imports:
            indent = ''
            for i in range(n.get_depth()):
                indent += "-"
            print '|-'+indent+ str(n)+'\n|'

        print "++++++++++++\n"
    
          
    def set_module_name (self,module_name):  
        """initially set the name of the top module
           NOT to be used later on"""
        self.unprocessed_imports.add(module_name)

    def get_module_name (self):
        """return the name of the top module"""
        if len(self.imports)>0:
            return self.imports[0].module_name

    def get_top_module (self):
        return self.get_import_by_name(self.module_name)

    def get_imports (self):
        return self.imports
    
    def get_axioms (self):
        axioms = self.imports.copy()
        axioms.discard(self.lemma_module) 
        return axioms
    
    def get_sorted_imports (self):
        l = list(self.imports)
        l.sort(ClifModule.compare)
        return l 
    
    def get_import_by_name (self, name):
        """Find and return a module from the list of imports by its module nam. """
        m = filter(lambda s:s.get_simple_module_name()==name, list(self.imports))
        if len(m)==0:
            raise ClifModuleSetError("Module {0} does not exist in ClifModuleSet {1}".format(name, self.module_name))
        elif len(m)>1:
            raise ClifModuleSetError("Multiple modules with name '{0}' exist in ClifModuleSet {1}".format(name, self.module_name))            
        elif len(m)==1:
            return m[0]
    
    def get_import_closure (self, module):
        """return the set of all direct and indirect imports."""
        import_names = set([])  # list of the names of modules directly or indirectly imported by module
        imports = set([module,])   # list of modules directly or indirectly imported by module
        new_imports = set(module.get_imports()) # list of the names of modules directly imported by module
        logging.getLogger(__name__).debug("new direct imports: " + str(new_imports))
        while len(new_imports)>0:
            name = new_imports.pop()
            i = self.get_import_by_name(name)
            import_names.add(name) 
            imports.add(i)
            new_imports.update(set(i.get_imports()).difference(import_names)) # add the imports that have not yet been processed
        imports = list(imports)
        imports.sort(ClifModule.compare)
        return imports
        
    
    def get_non_logical_symbol_info (self,symbol):
        """get relevant information about a nonlogical symbol"""        
    
    def update_nonlogical_symbols(self,new_nonlogical_symbols,depth):
        """update the ClifModuleSet's list of nonlogical symbols with the symbols in new_nonlogical_symbols
           new_nonlogical_symbols -- list of tuples (symbol_name, number of modules this occurs in, minimal_depth in import tree, maximal_depth in import tree)
         """
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
            
            
    def add_lemma_module (self, lemma_module):
        """Add a lemma module to this ClifModuleSet. If one already exists, the old one is overwritten."""
        self.module_name = lemma_module.get_simple_module_name()
        
        # delete old lemma module if one exists
        if self.lemma_module:
            self.imports.remove(self.lemma_module)
        else:
            for m in self.imports:
                m.depth = m.depth + 1
        self.lemma_module = lemma_module
        self.imports.add(lemma_module)
        return self.lemma_module
    
    def get_lemma_module (self):
        return self.lemma_module
        
    def remove_lemma_module (self):
        # delete old lemma module if one exists
        if self.lemma_module:
            self.imports.remove(self.lemma_module)
            for m in self.imports:
                m.depth = m.depth - 1
        self.lemma_module = None
        return True
    

    # extract the predicates and functions from prover9 mock run
    def extract_p9_predicates_and_functions (self):
    
        #print 'extract predicates and functions'
        prover9args = 'prover9 -t 0 -f '
        
    
        for f in self.imports:
            prover9args += f.p9_file_name + ' '
        
        options_file = commands.get_p9_optionsfile(self.get_module_name(), verbose=False)
        prover9args += ' ' + options_file + ' '

        
        # would be better to create a temporary file or read the output stream directly
        temp_file = self.get_module_name() + '_order' + filemgt.read_config('ladr','ending')
        prover9args += ' > ' + temp_file
        logging.getLogger(__name__).debug(prover9args)
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
        #print 'temp file : ' + temp_file
        #print 'options file : ' + options_file
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
        
        logging.getLogger(__name__).debug("all primitive predicates of " + self.module_name  + " : " + str(self.primitive_predicates))
        logging.getLogger(__name__).debug( "all defined predicates " + self.module_name  + " : " +  str(self.defined_predicates))
        logging.getLogger(__name__).debug( "all defined predicates " + self.module_name  + " : " + str(self.nonskolem_functions))
    
                
                
    def get_list_of_nonlogical_symbols (self, imports=None):
        """returns a simple list of nonlogical symbols without additional information.
        This is different from self.nonlogical_symbols, which stores additional information about frequency, depth, etc."""
        s = set([])
        if not imports:
            imports = self.imports
        
        for m in imports:
            s.update(m.get_nonlogical_symbols())
        return s
      
    
    
    def run_simple_consistency_check (self, module_name = None, modules = None, options_files = None):
        """ test the input for consistency by trying to find a model or an inconsistency."""
        # want to create a subfolder for the output files
        outfile_stem = filemgt.get_full_path(self.module_name, 
                                            folder=filemgt.read_config('output','folder')) 
        
        if not module_name:
            module_name = self.module_name
        
        if not modules: 
            modules = self.imports  # use all imports as default set of modules
        
        reasoners = ReasonerSet() 
        reasoners.constructAllCommands(modules, outfile_stem)
        logging.getLogger(__name__).info("USING " + str(len(reasoners)) + " REASONERS: " + str([r.name for r in reasoners]))
        
        # run provers and modelfinders simultaneously and wait until one returns
        reasoners = process.raceProcesses(reasoners)

        return_value = self.consolidate_results(reasoners)    

        if len(modules)==0:
            self.pretty_print_result(module_name + " (without imports)", return_value)
        else:
            self.pretty_print_result(module_name + " (with imports = " + str(modules) + ")", return_value)
        
        results = {tuple(modules): return_value}
        return results


    def run_full_consistency_check (self, modules = None, options_files = None, abort=True, abort_signal=CONSISTENT, increasing = False):
        """ test the input for consistency by trying to find a model or an inconsistency.
        If consistency is not established, check first individual modules for consistency and then increasingly larger subontologies.
        parameters:
        modules -- the set of modules to check consistency for; if not specified all modules of this ClifModuleSet will be used.
        option_files -- currently unused (default: None)
        abort -- boolean value indicating whether to abort when one set of modules return with the abort_signal (default: True).
        abort_signal -- code used to decide whether we are looking for a proof or an inconsistency (Default: ClifModuleSet.CONSISTENT).
        increasing -- boolean value indicating whether to start with the largest (increasing=False) or the smallest (increasing=True) sets of modules (default: False).   
        return value:
        dictionary with sets of imports as key and the return_code as value
        """

        if not modules:
            modules = self.imports
        
        # first do simple consistency check
        (m, return_value) = self.run_simple_consistency_check(modules= modules, options_files = options_files).popitem() 

        if return_value!=abort_signal or return_value==ClifModuleSet.UNKNOWN:
            safe_imports = self.get_consistent_modules()
            if len(safe_imports)==len(modules):
                logging.getLogger(__name__).info("No module of " + self.module_name + " is inconsistent.")
                # starting checking increasingly larger subontology, starting with the deepest ontologies first
                #self.run_consistency_check_by_depth()
                results = self.run_consistency_check_by_subset(modules = modules, 
                                                               options_files = options_files,
                                                               abort = abort, 
                                                               abort_signal = abort_signal, 
                                                               increasing= increasing)
            
        else:
            results = {tuple(modules): return_value}
        return results


    def run_consistency_check_by_subset (self, modules=None, options_files = None, abort=True, abort_signal=CONSISTENT, increasing = False):
        """run consistency checks by successively examining larger subontologies.
        parameters:
        modules -- the set of modules to check consistency for; if not specified all modules of this ClifModuleSet will be used.
        option_files -- currently unused (default: None)
        abort -- boolean value indicating whether to abort when one set of modules return with the abort_signal (default: True).
        abort_signal -- code used to decide whether we are looking for a proof or an inconsistency (Default: ClifModuleSet.CONSISTENT).
        increasing -- boolean value indicating whether to start with the largest (increasing=False) or the smallest (increasing=True) sets of modules (default: False).   
        return value:
        dictionary with sets of imports as key and the return_code as value
        """
        if not modules:
            modules = self.imports

        imports = list(modules)
        results = {}

        min_depth = 0

        max_depth = max(min_depth, max([s.get_depth() for s in imports]))

        if not self.lemma_module:
            max_depth += 1

        logging.getLogger(__name__).debug("STARTING consistency check by subset; max_depth=" + str(max_depth))
        if increasing:
            # starting with the smallest modules first
            ran = range(max_depth,min_depth,-1)
        else:
            ran = range(min_depth,max_depth,1)
        for reverse_depth in ran:
            #print "-----------------------"
            #print " LEVEL = " + str(reverse_depth)
            #print "-----------------------"
            current_imports = filter(lambda i:i.get_depth()==reverse_depth, imports)  # get all imports with reverse_depth level
            #print "-----------------------"
            #print "Next Try: " + str(current_imports)
            #print "-----------------------"
            for i in current_imports:
                tmp_imports = self.get_import_closure(i)
                if self.lemma_module:
                    tmp_imports.append(self.lemma_module)
                (i, r) = self.run_simple_consistency_check(i.get_simple_module_name(), tmp_imports, options_files=options_files).popitem()
                results[tuple(tmp_imports)] = r
                if r==ClifModuleSet.CONSISTENT:    # this set is consistent 
                    logging.getLogger(__name__).info("FOUND MODEL AT FOR SUBONTOLOGY IMPORT LEVEL " + str(reverse_depth))
                    if abort and abort_signal==ClifModuleSet.CONSISTENT: 
                        return results
                if r==ClifModuleSet.INCONSISTENT:    # this set is consistent 
                    logging.getLogger(__name__).info("FOUND PROOF FOR SUBONTOLOGY AT IMPORT LEVEL " + str(reverse_depth))
                    if abort and abort_signal==ClifModuleSet.INCONSISTENT:
                        return results
                
        return results   
        #self.run_simple_consistency_check(self.module_name)
            
        


    def run_consistency_check_by_depth (self, modules=None, options_files = None, abort=True, abort_signal=CONSISTENT, increasing = False):
        """run consistency checks by successively testing a larger subontology by increasing the depth cutoff.
        parameters:
        modules -- the set of modules to check consistency for; if not specified all modules of this ClifModuleSet will be used.
        option_files -- currently unused (default: None)
        abort -- boolean value indicating whether to abort when one set of modules return with the abort_signal (default: True).
        abort_signal -- code used to decide whether we are looking for a proof or an inconsistency (Default: ClifModuleSet.CONSISTENT).
        increasing -- boolean value indicating whether to start with the largest (increasing=False) or the smallest (increasing=True) sets of modules (default: False).   
        return value:
        dictionary with sets of imports as key and the return_code as value
        """
        if not modules:
            modules = self.imports

        imports = list(modules)
        results = {}
        
        if self.lemma_module:
            min_depth = 0
        else:
            min_depth = -1

        max_depth = max(min_depth, max([s.get_depth() for s in imports]))

        if increasing:
            # starting with the smallest modules first
            ran = range(max_depth,min_depth,-1)
        else:
            ran = range(min_depth,max_depth,1)

        for reverse_depth in ran:
            tmp_imports = self.get_consistent_module_set(modules=modules, min_depth=reverse_depth, max_depth=max_depth) 
            if self.lemma_module:
                tmp_imports.append(self.lemma_module)
            (i, r) = self.run_simple_consistency_check(module_name=str(tmp_imports), modules=tmp_imports, options_files=options_files).popitem()
            results[tuple(tmp_imports)] = r
            if r==ClifModuleSet.CONSISTENT:    # this set is consistent 
                logging.getLogger(__name__).info("FOUND MODEL AT DEPTH LEVEL " + str(reverse_depth))
                if abort and abort_signal==ClifModuleSet.CONSISTENT: 
                    return results
            if r==ClifModuleSet.INCONSISTENT:    # this set is consistent 
                logging.getLogger(__name__).info("FOUND PROOF AT DEPTH LEVEL " + str(reverse_depth))
                if abort and abort_signal==ClifModuleSet.INCONSISTENT:
                    return results

        return results   
        


    def get_consistent_module_set (self, modules=None, min_depth=0, max_depth=None):
        """get a set of all the imported modules that are between (inclusive) certain lower and upper depth levels"""
        imports = set([])

        if not modules:
            modules = self.imports

        for m in modules: 
            if max_depth:
                if m.get_depth()>=min_depth and m.get_depth()<=max_depth:
                    imports.add(m)
            elif m.get_depth()>=min_depth:
                imports.add(m)

        return imports
        
        

    def get_consistent_modules (self):
        """get a set of all the imported modules that are not provably inconsistent by themselves."""
        safe_imports = set([])

        for m in self.imports: # check each imported module for consistency
            m_return_value = self.run_module_consistency_check(m)
            if m_return_value == ClifModuleSet.INCONSISTENT:
                self.pretty_print_result(m.get_simple_module_name(), m_return_value)
            else:    # keep all imports that are consistent by themselves
                safe_imports.add(m)

        return safe_imports


    def run_module_consistency_check (self,module):
        """check a single module for consistency."""
        outfile_stem = filemgt.get_full_path(module.get_simple_module_name(), 
                                            folder=filemgt.read_config('output','folder')) 

        reasoners = ReasonerSet() 
        reasoners.constructAllCommands([module], outfile_stem)
        logging.getLogger(__name__).info("USING " + str(len(reasoners)) + " REASONERS: " + str([r.name for r in reasoners]))
        
        # run provers and modelfinders simultaneously and wait until one returns
        reasoners = process.raceProcesses(reasoners)

        return_value = self.consolidate_results(reasoners)    
        self.pretty_print_result(module.get_simple_module_name(), return_value)  
        
        
    def consolidate_results (self, reasoners):
        """ check all the return codes from the provers and model finders to find whether a model or inconsistency has been found.
        return values:
        consistent (1) -- model found, the ontology is consistent
        unknown (0) -- unknown result (no model and no inconsistency found)
        inconsistent (-1) -- an inconsistency has been found in the ontology
         """
        return_value = None
        successful_reasoner = None
         
        for r in reasoners:
            if not r.isProver() and r.terminatedSuccessfully():
                return_value = ClifModuleSet.CONSISTENT
                successful_reasoner = r.name
                logging.getLogger(__name__).debug("TERMINATED SUCCESSFULLY (" + str(r.return_code) + "): " + r.name) 
            if r.isProver() and r.terminatedSuccessfully():
                if not return_value==ClifModuleSet.CONSISTENT:
                    return_value = ClifModuleSet.PROOF
                    successful_reasoner = r.name
                else:
                    # problem: a proof and a counterexample have been found
                    return_value == ClifModuleSet.CONTRADICTION
                    logging.getLogger(__name__).critical("CONTRADICTORY RESULTS from " + self.module_name +': ' + r.name + ' and ' + successful_reasoner)
            if r.terminatedUnknowingly():
                logging.getLogger(__name__).info("UNKNOWN RESULT (" + str(return_value) + "): " + r.name)
    
        logging.getLogger(__name__).info("CONSOLIDATED RESULT: " + str(return_value))
        return return_value


    def pretty_print_result (self, module_name, return_value):
        """ render the results in a human readable format"""
        if self.lemma_module:
            return self.pretty_print_proof_result(module_name, return_value)
        else:
            return self.pretty_print_consistency_result(module_name, return_value)
        
        
    def pretty_print_consistency_result (self, module_name, return_value):
        """
        consistent (1) -- model found, the ontology is consistent
        unknown (0) -- unknown result (no model and no inconsistency found)
        inconsistent (-1) -- an inconsistency has been found in the ontology
        """
        if return_value==ClifModuleSet.CONSISTENT:  s="CONSISTENT"
        elif return_value==ClifModuleSet.INCONSISTENT: s="INCONSISTENT"
        elif return_value==ClifModuleSet.UNKNOWN or return_value==None: s="UNKNOWN"
        else: s="CONTRADICTION"
        
        logging.getLogger(__name__).info(s + " (return value = " + str(return_value) + "): " + module_name)


    def pretty_print_proof_result (self, module_name, return_value):
        """
        counterexample (-1) -- a counterexample has been found
        unknown (0) -- unknown result (no proof and no counterexample found)
        lemma (1) -- a proof has been found
        """
        if return_value==ClifModuleSet.COUNTEREXAMPLE:  s="COUNTEREXAMPLE"
        elif return_value==ClifModuleSet.PROOF: s="PROOF"
        elif return_value==ClifModuleSet.UNKNOWN or return_value==None: s="UNKNOWN"
        else: s="CONTRADICTION"

        logging.getLogger(__name__).info(s + " (return value = " + str(return_value) + "): " + module_name)

        
        
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
        
       
    def get_ladr_files (self, imports = None):
        """get a list of translations of all associated ClifModules in LADR syntax."""
        
        if not imports:
            imports = self.imports
        
        p9_files = []
        for m in imports:
            p9_files.append(m.get_p9_file_name())
        return p9_files

   
    def get_single_ladr_file (self, imports = None):
        """get the ClifModuleSet as a single file in LADR syntax."""

        # if the given imports are identical to the modules imports, treat it as the modules imports were used
        if imports and set(self.imports).issubset(imports) and set(self.imports).issuperset(imports):
            imports = None

        # avoid redundant work if we already have the ladr file
        if not imports and len(self.p9_file_name)>0:
            return self.p9_file_name

        ending = ""
        if not imports:
            ending = filemgt.read_config('ladr','all_ending')
            name = self.module_name
        else:
            ending = filemgt.read_config('ladr','select_ending')
            name = imports[0].get_simple_module_name()
        # construct the final ending
        ending += filemgt.read_config('ladr','ending')
        
        p9_files = self.get_ladr_files(imports)

        p9_file_name = filemgt.get_full_path(name, 
                                           folder=filemgt.read_config('ladr','folder'), 
                                           ending=ending)
        if not imports:
            self.p9_file_name = p9_file_name
            
        #print "FILE NAME:" + self.p9_file_name
        # TODO: need to initialize self.replaceable_symbols
        ladr.cumulate_ladr_files(p9_files, p9_file_name)
        logging.getLogger(__name__).info("CREATED SINGLE LADR TRANSLATION: " + p9_file_name)
        return p9_file_name
   

    def get_tptp_files (self, imports = None):
        """ get a list of translations of all associated ClifModules in TPTP syntax."""
        
        if not imports:
            imports = self.imports
        
        tptp_files = []
        for m in imports:
            tptp_files.append(m.get_tptp_file_name())
        return tptp_files
    

    def get_single_tptp_file (self, imports = None):
        """translate the module and all imported modules to a single TPTP file. Uses the LADR format as intermediate step."""
        
        # if the given imports are identical to the modules imports, treat it as the modules imports were used
        if imports and set(self.imports).issubset(imports) and set(self.imports).issuperset(imports):
            imports = None

        # avoid redundant work if we already have the tptp file
        if not imports and len(self.tptp_file_name)>0:
            return self.tptp_file_name

        p9_file_name = self.get_single_ladr_file(imports)

        ending = ""
        if not imports:
            ending = filemgt.read_config('tptp','all_ending')
            name = self.module_name
        else:
            ending = filemgt.read_config('tptp','select_ending')
            name = imports[0].get_simple_module_name()
        # construct the final ending
        ending += filemgt.read_config('tptp','ending')

        tptp_file_name = filemgt.get_full_path(name, 
                                           folder=filemgt.read_config('tptp','folder'), 
                                           ending=ending)

        if not imports:
            self.tptp_file_name = tptp_file_name
            
        ladr.translate_to_tptp_file(p9_file_name, 
                                    tptp_file_name, 
                                    self.get_list_of_nonlogical_symbols(imports))

        return tptp_file_name                


class ClifModuleSetError(Exception):
    
    output = []
    
    def __init__(self, value, output=[]):
        self.value = value
        self.output = output
        logging.getLogger(__name__).error(repr(self.value) + '\n\n' + (''.join('{}: {}'.format(*k) for k in enumerate(self.output))))
    def __str__(self):
        return repr(self.value) + '\n\n' + (''.join('{}: {}'.format(*k) for k in enumerate(self.output)))


        
if __name__ == '__main__':
    import sys
    # global variables
    options = sys.argv
    m = ClifModuleSet(options[1])
    #print m.get_single_tptp_file()
    #print m.get_top_module()
    print m.get_import_closure(m.get_top_module())
    #print m.get_import_closure(m.get_import_by_name("codi\codi_linear_int"))
