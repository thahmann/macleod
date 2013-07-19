'''
Created on 2012-03-07
Refactored on 2013-03-16

@author: Torsten Hahmann
'''
import os, logging, filemgt, process, clif, commands, ladr

class ClifModule(object):
   
    '''
    classdocs
    '''
    def __init__(self,name,depth=None):
        '''
        Constructor
        '''
        self.module_set = None
        
        self.module_name = ''
        
        self.hierarchy_name = ''
        
        """set of all imported module names """
        self.imports = set([])
        
        """ set of all parent module names"""
        self.parents = None
        self.ancestors = None
        
        self.clif_file_name = ''
        
        """Location of the clif input file that has undergone preprocessing"""
        self.clif_processed_file_name = ''
        
        self.p9_file_name = None
        
        self.tptp_file_name = None
        
        # the distinction between nonlogical_symbols and nonlogical_variables assumes that a single symbol is not used as both in different sentences
        self.nonlogical_symbols = set([])
        self.ancestors_nonlogical_symbols = None
        #self.parents_nonlogical_symbols = set([])
        
        # stores the depth of the import hierarchy
        self.depth = depth
        
        self.set_module_name(name)
        logging.getLogger(__name__).info('processing module: ' + self.module_name)
        # remove any obsolete URL prefix as specified in the configuration file
        if self.module_name.endswith(filemgt.read_config('cl','ending')):
            self.module_name = os.path.normpath(self.module_name.replace(filemgt.read_config('cl','ending'),''))
            
        self.hierarchy_name = filemgt.get_hierarchy_name(self.module_name)
            
        self.preprocess_clif_file()



    def preprocess_clif_file (self):
        # add the standard ending for CLIF files to the module name
        self.clif_file_name = filemgt.get_full_path(self.module_name, ending=filemgt.read_config('cl','ending'))
        print self.clif_file_name

        self.clif_processed_file_name = filemgt.get_full_path(self.module_name,
                                                      folder= filemgt.read_config('converters','tempfolder'),
                                                      ending = filemgt.read_config('cl','ending'))

        logging.getLogger(__name__).debug("Clif file name = " + self.clif_file_name)
        logging.getLogger(__name__).debug("Clif preprocessed file name = " + self.clif_processed_file_name)
        
        clif.remove_all_comments(self.clif_file_name,self.clif_processed_file_name)
        
        
        self.imports = clif.get_imports(self.clif_processed_file_name)
        
        logging.getLogger(__name__).debug("imports detected in " + self.module_name + ": " + str(self.imports))
        
        self.nonlogical_symbols = clif.get_all_nonlogical_symbols(self.clif_processed_file_name)
        

    def get_module_set (self, imports = None):
        """ return the set of modules (ClifModuleSet) to which this module belongs."""
        from src.ClifLemmaSet import LemmaModule
        #print "IMPORTS = " + str(imports)
        
        if self.module_set is not None:
            return self.module_set
        elif not isinstance(self, LemmaModule):
            logging.getLogger(__name__).error("Cannot determine ModuleSet for module " + self.module_name + " with imports " + str(imports))
        elif imports:
            for i in imports:
                if not isinstance(i, LemmaModule):
                    return i.module_set
            logging.getLogger(__name__).error("Cannot determine ModuleSet for lemma module " + self.module_name + " with imports " + str(imports))
        return None

    def set_module_name (self,name):
        self.module_name = filemgt.get_canonical_relative_path(name)
    
#     def get_full_module_name (self,module=None):
#         if not module:
#             module= self.module_name
#         import re
#         prefix = re.compile(re.escape(filemgt.read_config('cl','prefix')), re.IGNORECASE)
#         prefix.sub('', module)
#         return os.path.abspath(module)
                
    def get_hierarchy (self):
        return filemgt.get_hierarchy_name(self.module_name)
                
#     """ Called by ClifModuleSet so that each module knows all its direct parent modules.
#     """
#     def add_parents (self,name,depth):
#         #print "adding parent: " + str(name) + ' (' + str(depth) + ')' + ' to ' + self.module_name
#         self.parents.add(name)
#         self.parents_nonlogical_symbols.update(self.module_set.get_import_by_name(name).get_nonlogical_symbols())
#         # update the depth
#         if depth>=self.depth:
#             self.depth=depth+1
#             #print "new depth = " + str(self.depth)
        
    def get_parents (self):
        if not self.parents:
            self.parents = set([])
            for module in self.module_set.imports:
                if self.module_name in module.imports:
                    self.parents.add(module.module_name)
#                     if self.depth<=module.depth:
#                         self.depth=module.depth+1
#                         print "new depth = " + str(self.depth)
        return self.parents
            
    def get_imports (self):
        """returns the set of immediate imports."""
        return self.imports
        
    def get_nonlogical_symbols (self):
        return self.nonlogical_symbols
    
    def get_ancestors (self):
        if not self.ancestors:
            self.ancestors = set([])
            for parent in self.get_parents():
                self.ancestors.update(self.get_module_set().get_import_closure(self.get_module_set().get_import_by_name(parent)))
        return self.ancestors
    
    def get_ancestors_nonlogical_symbols (self):
        if not self.ancestors_nonlogical_symbols:
            self.ancestors_nonlogical_symbols = set([])
            for ancestor in self.get_ancestors():
                self.ancestors_nonlogical_symbols.update(ancestor.get_nonlogical_symbols())
        return self.ancestors_nonlogical_symbols
    
        
    def get_depth (self):
        """determines and returns the shortest depth, i.e. the shortest distance between this module and the root module."""
        if not self.depth:
            self.depth = 0
            ancestor_set = set([self])
            while self.get_module_set().get_top_module() not in ancestor_set:
                #print ancestor_set
                self.depth += 1
                new_ancestors = [a.get_parents() for a in ancestor_set]
                ancestor_set.update([self.get_module_set().get_import_by_name(a) for ancestors in new_ancestors for a in ancestors])
        return self.depth
                
    def __repr__ (self):
        return self.module_name

    def __str__(self):
        return (self.module_name
                + ' (depth=' + str(self.get_depth())
                + ', parents: ' + str(self.get_parents()) + ')')

    def shortstr(self):
        return self.__repr__()


    @staticmethod
    def compare(x, y):
        """ Compares two ClifModules to sort them first by depth (increasing) and then by name."""
        if x.get_depth() > y.get_depth():
           return 1
        elif x.get_depth() == y.get_depth():
           if x.module_name > y.module_name: return 1
           else: return -1
        else: #x < y
           return -1

    def __eq__(self, other):
        """checking whether the module is identical to another module based on name, depth, imports, and parents."""
        if not isinstance(other, ClifModule):
            return False
        # first compare name and depth
        elif self.module == other.module_name and self.depth == other.depth:
            # simple length checks to avoid unnecessary work
            if len(self.imports)!=len(other.imports):
                return False
            if len(self.get_parents())!=len(other.get_parents()):
                return False
            # base case (no other imports)
            if len(self.imports)==1:
                return True
            # compare the imports
            for i in self.imports:
                if i not in other.imports:
                    return False
            for i in other.imports:
                if i not in self.imports:
                    return False
            # compare the parents
            for i in self.get_parents():
                if i not in other.get_parents():
                    return False
            for i in other.get_parents():
                if i not in self.get_parents():
                    return False
        # if we made it here, name, depth, imports, and parents are identical
        return True


    def __ne__ (self, other):
        return not self.eq(other)


    def get_p9_file_name (self):
        """get the filename of the LADR translation of the module and translate the ClifModule if not yet done so."""
        if not self.p9_file_name: # do the translation
            self.p9_file_name = filemgt.get_full_path(self.module_name,
                                                       folder=filemgt.read_config('ladr','folder'),
                                                       ending=filemgt.read_config('ladr','ending'))
            cmd = commands.get_clif_to_ladr_cmd(self)
            process.executeSubprocess(cmd)
            logging.getLogger(__name__).info("CREATED LADR TRANSLATION: " + self.p9_file_name)
            
            p9_file = open(self.p9_file_name,'r')
            lines = p9_file.readlines()
            p9_file.close()
            lines = ladr.comment_imports(lines)
            #print "".join(lines)
            p9_file = open(self.p9_file_name,'w')
            p9_file.writelines(lines)
            p9_file.close()
            logging.getLogger(__name__).debug("COMMENTED IMPORTS IN LADR FILE: " + self.p9_file_name)
             
        return self.p9_file_name


    def get_tptp_file_name (self):
        """get the filename of the TPTP translation of the module and translate the ClifModule if not yet done so.
        This version does not rely on the clif to ladr translation, but does a direct translation."""
        
        if not self.tptp_file_name:
            self.tptp_file_name = filemgt.get_full_path(self.module_name,
                                                       folder=filemgt.read_config('tptp','folder'),
                                                       ending=filemgt.read_config('tptp','ending'))
            
            tptp_sentences = clif.to_tptp([self.clif_processed_file_name])
            tptp_file = open(self.tptp_file_name, 'w')
            tptp_file.writelines([t+"\n" for t in tptp_sentences])
            tptp_file.close()

            logging.getLogger(__name__).info("CREATED TPTP TRANSLATION: " + self.tptp_file_name)
             
        return self.tptp_file_name
    
    """find definitions that introduce no new symbols or more than one new symbol. 
    """
    def detect_faulty_definitions (self):
        if  filemgt.get_type(self.module_name)== filemgt.read_config('cl','definitions_folder'):
            properly_defined_symbols = set([])
            new_symbols = []
            i = 0
            sentences = clif.get_sentences_from_file(self.clif_file_name)
            if len(sentences)==0:
                logging.getLogger(__name__).warn("Empty definition file: " + self.module_name)
            else:
                new_symbols = [clif.get_nonlogical_symbols(sentence) - self.get_ancestors_nonlogical_symbols() for sentence in clif.get_sentences_from_file(self.clif_file_name)]

                # check for definitions that introduce no new symbols
                for i in range(0,len(new_symbols)):
                    if len(new_symbols[i])==0:
                        logging.getLogger(__name__).error("No new symbol seen in definition " + str(i) + " in: " + self.module_name)
                
                while True:
                    # filter the definitions that have exactly one defined symbol
                    new_symbols = [(sym - properly_defined_symbols) for sym in new_symbols]
                    new_single_symbols = [sym[0] for sym in new_symbols if len(sym)==1]
                    if len(new_single_symbols)==0:
                        break;
                    properly_defined_symbols.update(new_single_symbols)

                # the remaining ones have two or more newly introduced symbols
                for i in range(0,len(new_symbols)):
                    logging.getLogger(__name__).error("More than one new symbol (" + str(new_symbols[i]) + ") found in a definition in: " + self.module_name)				
        
        
    def verify_hierarchy_symbols(self):
        parents_hierarchies = [p.get_hierarchy() for p in self.get_parents()]
        if self.get_hierarchy() in parents_hierarchies:
            if len(self.nonlogical_symbols - self.get_ancestors_nonlogical_symbols())>0:
                logging.getLogger(__name__).warn("Found some nonlogical symbols (" + str(self.nonlogical_symbols - self.get_ancestors_nonlogical_symbols()) + ") not present in any imported ontology even though the new ontology " + self.module_name + " resides in the same hierarchy as one of the imported ontologies (" + self.get_hierarchy() + ").  This may be due to an implicitely defined symbol, but should be examined.")
                return False
            else:
                return True
        