'''
Created on 2012-03-07
Refactored on 2013-03-16

@author: Torsten Hahmann
'''

import macleod.Filemgt as filemgt
import macleod.Process as process
import macleod.Clif as clif
import macleod.Commands as commands
import macleod.Ladr as ladr

import os, logging

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
        self.import_closure_nonlogical_symbols = None

        self.properly_defined_symbols = None
        #self.parents_nonlogical_symbols = set([])

        # stores the depth of the import hierarchy
        self.depth = depth

        self.set_module_name(name)
        logging.getLogger(__name__).info('processing module: ' + self.module_name)
        # remove any obsolete URL ending as specified in the configuration file
        if self.module_name.endswith(filemgt.read_config('cl','ending')):
            self.module_name = os.path.normpath(self.module_name.replace(filemgt.read_config('cl','ending'),''))

        self.hierarchy_name = filemgt.get_hierarchy_name(self.module_name)

        self.preprocess_clif_file()

    def preprocess_clif_file (self):
        # add the standard ending for CLIF files to the module name
        self.clif_file_name = filemgt.get_full_path(self.module_name, ending=filemgt.read_config('cl','ending'))
        #print self.clif_file_name

        self.clif_processed_file_name = filemgt.get_full_path(self.module_name,
                                                      folder= filemgt.read_config('converters','tempfolder'),
                                                      ending = filemgt.read_config('cl','ending'))

        logging.getLogger(__name__).debug("Clif file name = " + self.clif_file_name)
        logging.getLogger(__name__).debug("Clif preprocessed file name = " + self.clif_processed_file_name)

        clif.remove_all_comments(self.clif_file_name, self.clif_processed_file_name)


        self.imports = clif.get_imports(self.clif_processed_file_name)

        logging.getLogger(__name__).debug("imports detected in " + self.module_name + ": " + str(self.imports))

        self.nonlogical_symbols = clif.get_all_nonlogical_symbols(self.clif_processed_file_name)


    def get_module_set (self, imports = None):
        """ return the set of modules (ClifModuleSet) to which this module belongs."""
        from macleod.ClifLemmaSet import LemmaModule
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

    def get_parents_as_modules (self):
        """ Return a set of parents as modules """
        parent_names = self.get_parents()
        return [self.module_set.get_import_by_name(i) for i in parent_names]

    """returns the set of immediate imports."""
    def get_imports (self):
        return self.imports

    def get_imports_as_modules (self):
        return [self.module_set.get_import_by_name(i) for i in self.imports]

    """ return a set of a (symbol, arity) tuples for all nonlogical symbols found in this particular clif module (not considering imports."""
    def get_nonlogical_symbols (self):
        return [(symbol, clif.get_nonlogical_symbol_arity_from_file(self.clif_processed_file_name,symbol)) for symbol in self.nonlogical_symbols]

#     def get_ancestors (self):
#         if not self.ancestors:
#             self.ancestors = set([])
#             for parent in self.get_parents():
#                 self.ancestors.update(self.get_module_set().get_import_closure(self.get_module_set().get_import_by_name(parent)))
#         return self.ancestors

    """ gets a set of (symbol, arity) tuples for all nonlogical symbols that are used in this module or any of the directly or indirectly imported modules.  This module can only be called once all imports have been processed."""
    def get_import_closure_nonlogical_symbols (self):
        if not self.module_set.completely_processed:
            logging.getLogger(__name__).error("Trying to access nonlogical symbols before completely processing all imports")
            return False
        if not self.import_closure_nonlogical_symbols:
            self.import_closure_nonlogical_symbols = set([])

            import_closure = self.get_module_set().get_import_closure(self)
            #print "IMPORT CLOSURE: " + str(import_closure)
            for i in import_closure:
                self.import_closure_nonlogical_symbols.update(i.get_nonlogical_symbols())
        return self.import_closure_nonlogical_symbols

    """ get a set of all nonlogical symbols (without arity) that are used in any of this module's directly or indirectly imported modules."""
    def get_irreflexive_import_closure_nonlogical_symbols (self):
        if not self.module_set.completely_processed:
            logging.getLogger(__name__).error("Trying to access nonlogical symbols before completely processing all imports")
            return False
        import_closure_nonlogical_symbols = set([])
        for i in self.get_imports_as_modules():
            #print i.module_name + " USES THE NONLOGICAL SYMBOLS " + str(i.get_import_closure_nonlogical_symbols())
            import_closure_nonlogical_symbols.update(i.get_import_closure_nonlogical_symbols())
        import_closure_nonlogical_symbols = set([symbol for (symbol, _) in import_closure_nonlogical_symbols])
        return import_closure_nonlogical_symbols

    """ gets all nonlogical symbols that are used in this module but not in any of the directly or indirectly imported modules."""
    def get_new_nonlogical_symbols (self):
        if not self.module_set.completely_processed:
            logging.getLogger(__name__).error("Trying to access nonlogical symbols before completely processing all imports")
            return False
        print("Import closure nonlogical symbols: " + str(self.get_import_closure_nonlogical_symbols()))
        print("Import closure nonlogical symbols: " + str(self.get_irreflexive_import_closure_nonlogical_symbols()))
        return self.get_import_closure_nonlogical_symbols() - self.get_irreflexive_import_closure_nonlogical_symbols()


    def get_depth (self):
        """determines and returns the shortest depth, i.e. the shortest distance between this module and the root module that (indirectly) imports this module."""
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
        long_repr = (self.module_name
                + ' (depth=' + str(self.get_depth())
                + ', parents: ' + str(self.get_parents()))

        long_repr +=  ')'
        long_repr += '\n'

        if self.module_set.completely_processed:
            if filemgt.module_is_definition_set(self.module_name) and not self.detect_faulty_definitions():
                long_repr += '| '
                for _ in range(self.get_depth()):
                    long_repr += '    '
                long_repr += '  + Defines symbols:'
                for (symbol, arity) in self.get_defined_symbols():
                    long_repr += ' ' + str(symbol) + '(' + str(arity) +')'
                long_repr += '\n'
        long_repr += '| '
        for _ in range(self.get_depth()):
            long_repr += '    '
        long_repr += '  + Uses symbols: '
        for (symbol, arity) in self.get_nonlogical_symbols():
            long_repr += ' ' + str(symbol) + '(' + str(arity) +')'
        return long_repr

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
        elif self.module_name == other.module_name and self.depth == other.depth:
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

    def __hash__(self):
        """Hashable implementation"""

        return id(self)


    def __ne__ (self, other):
        return not self.eq(other)


    def get_p9_file_name (self):
        """get the filename of the LADR translation of the module and translate the ClifModule if not yet done so."""
        if not self.p9_file_name: # do the translation
            self.p9_file_name = filemgt.get_full_path(self.module_name,
                                                       folder=filemgt.read_config('ladr','folder'),
                                                       ending=filemgt.read_config('ladr','ending'))
            self.get_translated_file(self.p9_file_name, "LADR")
            logging.getLogger(__name__).info("CREATED LADR TRANSLATION: " + self.p9_file_name)
        return self.p9_file_name


    def get_tptp_file_name (self):
        """get the filename of the TPTP translation of the module and translate the ClifModule if not yet done so.
        This version does not rely on the clif to ladr translation, but does a direct translation."""

        if not self.tptp_file_name:
            self.tptp_file_name = filemgt.get_full_path(self.module_name,
                                                       folder=filemgt.read_config('tptp','folder'),
                                                       ending=filemgt.read_config('tptp','ending'))

            self.get_translated_file(self.tptp_file_name, "TPTP")
            logging.getLogger(__name__).info("CREATED TPTP TRANSLATION: " + self.tptp_file_name)
        return self.tptp_file_name

    def get_translated_file(self, output_file_name, language):
#        try:
        sentences = clif.translate_sentences([self.clif_processed_file_name], language)
        output_file = open(output_file_name, 'w')
        output_file.writelines([t+"\n" for t in sentences])
        output_file.close()
        return True
#        except:
#            logging.getLogger(__name__).error("PROBLEM CREATING TRANSLATION: " + str(output_file_name))


    """
    Find sentences in a definitional module (in the current module only) that are obviously faulty, e.g. that introduce no new symbols or that introduce more than one new symbol. 
    It does not check whether a specific definition is an explicit definition (of the form P(x,...) <=> ...) or whether the newly defined symbols are completely defined.
    Return False if the module is not a definition.     
    """
    def detect_faulty_definitions (self):
        if self.properly_defined_symbols:
            return False

        faulty = False
        if  filemgt.module_is_definition_set(self.module_name):
            self.properly_defined_symbols = set([])
            new_symbols = []
            i = 0
            sentences = clif.get_logical_sentences_from_file(self.clif_processed_file_name)
            if len(sentences)==0:
                if len(self.imports)==0: 
                    logging.getLogger(__name__).warn("Empty definition file: " + self.module_name)
            else:
                #print "PARENT's IMPORT CLOSURE SYMBOLS: " + str(self.get_irreflexive_import_closure_nonlogical_symbols())
                #print "SENTENCE SYMBOLS: " + str(clif.get_nonlogical_symbols(sentences[0]))
                new_symbols = [clif.get_nonlogical_symbols(sentence) - self.get_irreflexive_import_closure_nonlogical_symbols() for sentence in sentences]
                #new_symbols = [clif.get_nonlogical_symbols(sentence) - self.get_irreflexive_import_closure_nonlogical_symbols() for sentence in sentences]
                #print new_symbols

                # check for definitions that introduce no new symbols
                for i in range(0,len(new_symbols)):
                    if len(new_symbols[i])==0:
                        logging.getLogger(__name__).error("No new symbol seen in definition " + str(i+1) + " in: " + self.module_name)
                        faulty = True

                while True:
                    # filter the definitions that have exactly one defined symbol
                    #print "NEW SYMBOLS = " + str(new_symbols)
                    new_symbols = [x - self.properly_defined_symbols for x in new_symbols]
                    new_single_symbols = [sym.pop() for sym in new_symbols if len(sym)==1]
#                    new_single_symbols = [sym.pop() for sym in filter(lambda x:len(x)==1, new_symbols)]
                    if len(new_single_symbols)==0: # stable set of single symbols
                        break;
                    self.properly_defined_symbols.update(new_single_symbols)

                # the remaining ones have two or more newly introduced symbols
                for i in range(0,len(new_symbols)):
                    if len(new_symbols[i])>0:
                        logging.getLogger(__name__).error("More than one new symbol (" + str(new_symbols[i]) + ") found in a definition in: " + self.module_name)
                        faulty = True
                #print "PROPERLY DEFINED SYMBOLS = " + str(self.properly_defined_symbols)

        return faulty				

    """
    Returns a list of the defined symbols if this module is a definition (based on its path) and contains no obviously faulty definitions.
    Each entry in the list is a tuple of the form (symbol, arity).
    """
    def get_defined_symbols (self):
        # get all definitions from this module if it is a definition
        defined_symbols = []
        if  filemgt.module_is_definition_set(self.module_name):
            if not self.detect_faulty_definitions():
                #print "DEFINED SYMBOLS = " + str(self.properly_defined_symbols)
                #logging.getLogger(__name__).info("Determining arity for symbols in " + self.module_name)
                for symbol in self.properly_defined_symbols:
                    #logging.getLogger(__name__).info("Determining arity for symbol: " + symbol)
                    arity = clif.get_nonlogical_symbol_arity_from_file(self.clif_processed_file_name, symbol)
                    defined_symbols.append((symbol, arity))
        return defined_symbols 

    """
    Checks whether this module is a definition.  
    The check is based only on its path and on the fact that each sentence has exactly one undefined symbol.
    """
    def is_simple_definition (self):
        if filemgt.module_is_definition_set(self.module_name) and not self.detect_faulty_definitions():
            return True
        else:
            return False

#     """check whether an ontology that is in the same hierarchy as one of the imported modules does not introduce new nonlogical symbols."""
#     def verify_hierarchy_symbols(self):
#         for p in self.get_parents():
#             if p.get_hierarchy()==self.get_hierarchy():
#                 # this module is in the same hierarchy as one of its parents
#                 if filemgt.module_is_axiom_set(self.module_name):
#                     
#             
#         
#         parents_hierarchies = [p.get_hierarchy() for p in self.get_parents()]
#         if self.get_hierarchy() in parents_hierarchies:
#             if len(self.nonlogical_symbols - self.get_ancestors_nonlogical_symbols())>0:
#                 logging.getLogger(__name__).warn("Found some nonlogical symbols (" + str(self.nonlogical_symbols - self.get_ancestors_nonlogical_symbols()) + ") not present in any imported ontology even though the new ontology " + self.module_name + " resides in the same hierarchy as one of the imported ontologies (" + self.get_hierarchy() + ").  This may be due to an implicitely defined symbol, but should be examined.")
#                 return False
#             else:
#                 return True

