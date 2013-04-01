'''
Created on 2013-03-31

@author: Torsten Hahmann
'''

import sys
from src import *
import filemgt, process, clif, commands, ladr
from src.ReasonerSet import * 
import os, datetime, logging

class LemmaModule(ClifModule):

    '''
    classdocs
    '''
    def __init__(self, module_name, ladr_file_name):
        '''
        Constructor
        '''
        
        self.p9_file_name = ladr_file_name

        # remove any obsolete URL prefix as specified in the configuration file
        #if ladr_file_name.endswith(filemgt.read_config('ladr','ending')):
        #super(LemmaModule, self).__init__(name,0)
        
        self.module_name = module_name


        logging.getLogger(self.__module__ + "." + self.__class__.__name__).info('constructing lemma module: ' + self.module_name)
        
        # stores the depth of the import hierarchy
        #self.depth = 0



class ClifLemmaSet(object):

    module = None

    lemmas = []
    
    p9_file_name = ''
    
    tptp_file_name = ''
    
    def __init__ (self, name):
        
        self.module = ClifModule(name,0)
        logging.getLogger(__name__).info('constructed clif module for lemma file: ' + self.module.module_name)
        
        self.lemmas = []
        self.add_lemmas()

    
    def get_number_of_lemmas (self):
        return len(lemmas)


    def add_lemmas (self):
        
        # first get LADR translation of ClifModule

        # logging.getLogger(__name__).debug("CREATING LADR TRANSLATION OF LEMMA: " + self.module.module_name)
        
        logging.getLogger(__name__).debug("CREATED LADR TRANSLATION OF LEMMA: " + self.module.get_p9_file_name())
        
        #self.module.get_p9_file_name()
                
        (lemma_names, ladr_files) = ladr.get_ladr_goal_files(self.module.p9_file_name, self.module.module_name)

        # populate the list of lemmas        
        for n in ladr_files:
            name = os.path.join(os.path.dirname(self.module.module_name),
                                os.path.basename(n.replace(filemgt.read_config('ladr','ending'),'')))
            m = LemmaModule(name,n)
            self.lemmas.append(m)
        
    def get_lemmas (self):
        return self.lemmas
