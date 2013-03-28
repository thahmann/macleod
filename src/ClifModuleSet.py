'''
Created on 2010-11-05
Regrouped all methods that pertain to an import hierarchy into the new module ClifModuleSet on 2013-03-15

@author: Torsten Hahmann
'''

import sys
from src import *
from src.ReasonerSet import * 
import os, datetime
#import atexit


class ClifModuleSet(object):

    module_name = ''

    # list of ClifModules that are imported and have been processed already   
    imports = set([])
    
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
    
    reasoners = []
    
    provers = {}
    finders = {}

    # initialize with a set of files to be processed (for lemmas)
    def __init__(self, name):
        
        m = ClifModule(name,0)
        self.imports.add(m)
        self.module_name=m.get_simple_module_name()

        self.unprocessed_imports = self.unprocessed_imports.union(m.get_imports())

        while len(self.unprocessed_imports)>0:
            m = ClifModule(self.unprocessed_imports.pop(),0)
            
            # Link the module to all its parents
            for cm in self.imports:
                if m.get_simple_module_name() in cm.get_imports():
                    m.add_parent(cm.get_simple_module_name(),cm.get_depth())

            self.imports.add(m)

            # add all the names of imported modules that have not yet been processed
            new_imports = set(m.get_imports()) - set([i.get_simple_module_name() for i in self.imports])
            for i in new_imports:
                print '|-- imports: ' + m.get_simple_module_name(i) + ' (depth ' + str(m.get_depth()+1) + ')'
                            
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
        #print "direct imports: " + str(new_imports)
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
        print prover9args
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
        
        print 'all primitive predicates: ' + str(self.primitive_predicates)
        print 'all defined predicates: ' + str(self.defined_predicates)
        print 'all functions: ' + str(self.nonskolem_functions)
    
                
                
    def get_list_of_nonlogical_symbols (self):
        """returns a simple list of nonlogical symbols without additional information.
        This is different from self.nonlogical_symbols, which stores additional information about frequency, depth, etc."""
        s = set([])
        for m in self.imports:
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
        
        self.reasoners = ReasonerSet() 
        self.reasoners.constructAllCommands(modules, outfile_stem)
        
        # run provers and modelfinders simultaneously and wait until one returns
        self.reasoners = process.raceProcesses(self.reasoners)

        return_value = self.consolidate_results(self.reasoners)    

        if len(modules)==0:
            self.pretty_print_consistency_result(module_name + " (without imports)", return_value)
        else:
            self.pretty_print_consistency_result(module_name + " (with imports = " + str(modules) + ")", return_value)
        
        return return_value


    def run_full_consistency_check (self, modules = None, options_files = None):
        """ test the input for consistency by trying to find a model or an inconsistency.
        If consistency is not established, check first individual modules for consistency and then increasingly larger subontologies."""

        if not modules:
            modules = self.imports
        
        # first do simple consistency check
        return_value = self.run_simple_consistency_check(modules= modules, options_files = options_files)   

        if return_value==-1 or return_value==0:
            safe_imports = self.get_consistent_modules()
            if len(safe_imports)==len(modules):
                print "All modules are consistent."
                # starting checking increasingly larger subontology, starting with the deepest ontologies first
                #self.run_consistency_check_by_depth()
                self.run_consistency_check_by_subset()

    def run_consistency_check_by_subset (self, modules=None):
        """run consistency checks by successively examining larger subontologies."""
        if not modules:
            modules = self.imports

        imports = list(modules)
        # start with the second deepest depth and examine each ontology and its imports
        max_depth = max(0, max([s.get_depth() for s in imports]))
        print "max_depth=" + str(max_depth)
        for reverse_depth in range(max_depth,0,-1):
            current_imports = filter(lambda i:i.get_depth()==reverse_depth, imports)  # get all imports with reverse_depth level
            for i in current_imports:
                self.run_simple_consistency_check(i.get_simple_module_name(), self.get_import_closure(i))
        #self.run_simple_consistency_check(self.module_name)
            
        


    def run_consistency_check_by_depth (self, modules=None):
        """run consistency checks by successively testing a larger subontology by increasing the depth cutoff."""
        imports = list(modules)
        max_depth = max([s.get_depth() for s in imports])
        for reverse_depth in range(max_depth,0,-1):
            s = self.get_consistent_module_set(modules=modules, min_depth=reverse_depth, max_depth=max_depth) 
            return_value = self.run_simple_consistency_check(module_name=str(s), modules=s, options_files=options_files)
            if return_value==-1:    # this set is inconsistent
                print "Found inconsistent subontology."
                break                
        


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
        """get a set of all the imported modules that are provably consistent by themselves."""
        safe_imports = set([])

        for m in self.imports: # check each imported module for consistency
            m_return_value = self.run_module_consistency_check(m)
            if m_return_value == -1:
                self.pretty_print_consistency_result(m.get_simple_module_name(), m_return_value)
            else:    # keep all imports that are consistent by themselves
                safe_imports.add(m)

        return safe_imports


    def run_module_consistency_check (self,module):
        """check a single module for consistency."""
        outfile_stem = filemgt.get_full_path(module.get_simple_module_name(), 
                                            folder=filemgt.read_config('output','folder')) 
        
        (provers, finders) = self.select_systems([module,], outfile_stem)
        
        # run provers and modelfinders simultaneously and wait until one returns
        (prc, frc) = process.raceProcesses(provers, finders)

        return_value = self.consolidate_results(provers, finders)
        self.pretty_print_consistency_result(module.get_simple_module_name(), return_value)  
        
        

    def consolidate_results(self, reasoners):
        """ check all the return codes from the provers and model finders to find whether a model or inconsistency has been found
        return values:
        consistent (-1) -- an inconsistency has been found in the ontology
        unknown (0) -- unknown result (no model and no inconsistency found)
        inconsistent (1) -- model found, the ontology is consistent
         """
        return_value = 0
         
        for r in reasoners:
            if not r.isProver() and r.terminatedSuccessfully:
                return_value = 1
            elif r.isProver() and r.terminatedSuccessfully:
                if not return_value==1:
                    return_value = -1
                else:
                    # problem: a proof and a counterexample have been found
                    return_value == -100 
            elif r.terminatedUnknowingly:
                print finder + ' returned with unknown result, return code ' + str(rc)
    
        return return_value
        
    def pretty_print_consistency_result (self, module_name, return_value):
        if return_value==-1:  s="inconsistent"
        elif return_value==1: s="consistent"
        elif return_value==0: s="unknown"
        else: s="contradiction"
        print str(module_name) + ": " + s
        
        
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
        
       
    def get_ladr_files (self):
        """get a list of translations of all associated ClifModules in LADR syntax."""
        p9_files = []
        for m in self.imports:
            p9_files.append(m.get_p9_file_name())
        return p9_files
   
    def get_single_ladr_file (self):
        """get the ClifModuleSet as a single file in LADR syntax."""
        import ladr
        p9_files = self.get_ladr_files()

        self.p9_file_name = filemgt.get_full_path(self.module_name, 
                                           folder=filemgt.read_config('ladr','folder'), 
                                           ending=filemgt.read_config('ladr','all_ending'))
        # TODO: need to initialize self.replaceable_symbols
        ladr.cumulate_ladr_files(p9_files, self.p9_file_name)
        print "CREATED LADR TRANSLATION: " + self.p9_file_name
        return self.p9_file_name
   

    def get_single_tptp_file (self):
        """translate the module and all imported modules to a single TPTP file. Uses the LADR format as intermediate step."""
        import ladr

        self.get_single_ladr_file()

        # hack: replace iff's (<->) by <- to do a correct windows translation; revert it afterwards
        ladr.replace_equivalences(self.p9_file_name)
        
        # convert LADR file to lower case, only temporarily for TPTP translation
        file = open(self.p9_file_name, 'r')
        text = file.readlines()
        file.close()
        file = open(self.p9_file_name, 'w')
        text = [s.strip().lower() for s in text]
        newtext = []
        for s in text:
            if len(s)>0: newtext.append(s+'\n')
        file.writelines(newtext)
        file.close()
        #print "".join(newtext)

        self.tptp_file_name = filemgt.get_full_path(self.module_name,
                                                    folder=filemgt.read_config('tptp','folder'),
                                                    ending=filemgt.read_config('tptp','all_ending'))
        
        cmd = commands.get_ladr_to_tptp_cmd(self.p9_file_name, self.tptp_file_name)
        process.executeSubprocess(cmd)  

        ladr.number_tptp_axioms(self.tptp_file_name)

        # complete hack
        ladr.replace_equivalences_back(self.tptp_file_name)

        # restore LADR file with proper case and equivalences
        self.get_single_ladr_file()
        
        print "CREATED TPTP TRANSLATION: " + self.tptp_file_name
        
        self.tptp_file_name = ladr.get_lowercase_tptp_file(self.tptp_file_name, self.get_list_of_nonlogical_symbols())
        return self.tptp_file_name    



#    # delete unnecessary files at the end
#    def cleanup(self):
#        if self.tidy:          
#            LADR.cleanup_option_files()  
#            for m in self.imports:
#                if os.path.exists(m.p9_intermediary_file_name):
#                    os.remove(m.p9_intermediary_file_name)
#                if os.path.exists(m.clif_processed_file_name):
#                    os.remove(m.clif_processed_file_name)
            


class ClifModuleSetError(Exception):
    
    output = []
    
    def __init__(self, value, output=[]):
        self.value = value
        self.output = output
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
