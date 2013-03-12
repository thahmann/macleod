'''
Created on 2012-10-18

@author: Torsten Hahmann
'''

from ColoreFileManager import ColoreFileManager
from LADR import LADR
import subprocess

class ClifModule(object):

    URL_PREFIX = 'http://stl.mie.utoronto.ca/colore'
    
    CLIF_TO_PROVER9 = '/stl/tmp/cltools/bin/clif-to-prover9'
    
    CLIF_ENDING = '.clif'
    
    
    '''
    classdocs
    '''

    def __init__(self,coloreprover,module_name,depth):
        '''
        Constructor
        '''
        self.clif = True
        self.coloreprover = None
        self.nonlogical_symbols = []
        self.nonlogical_variables = []
        self.coloreprover = coloreprover
        self.module_name = module_name.lower().replace(ClifModule.URL_PREFIX,'')
        self.depth = depth
        print 'processing module: ' + self.module_name
        
        self.clif_file_name = module_name + ClifModule.CLIF_ENDING
        self.replace_clif_quotes()
        self.get_nonlogical_symbols()
        
        self.p9_file_name = self.get_p9_file_name()
        print 'created p9 file: ' + self.p9_file_name
        #print 'all named entities : ' + str(namedentities)
        
        if self.clif:
            self.p9_intermediary_file_name = ColoreFileManager.get_name_with_subfolder(self.module_name, ColoreFileManager.GENERATED_FOLDER, '.p9i')
            ctp = subprocess.Popen(ClifModule.CLIF_TO_PROVER9 + ' ' +  self.clif_processed_file_name + ' > ' + self.p9_intermediary_file_name, shell=True)
            ctp.wait()
        #print module_name + ': '
        #print 'named entities in \'' + module_name + '\': ' + str(namedentities) 
        self.write_p9_file()
        
        # push nonlogical symbols and variables upwards (VERY LAST STEP)
#        if isinstance(parent, ClifModule):
#            parent.nonlogical_symbols.append[self.nonlogical_symbols]
#            parent.nonlogical_variables.append[self.nonlogical_variables]

        # cleanse the list of non-logical symbols
        for l in self.nonlogical_variables:
            for symbol in self.nonlogical_symbols:
                if l == symbol:
                    self.nonlogical_symbols.remove(symbol)
        
        self.coloreprover.append_nonlogical_symbols(self.nonlogical_symbols,self.depth)
        
        
    # replace all " by ' to prepare a clif file for translation to prover9 (LADR) syntax
    # also remove attribution (multiline comment) in clif file: \* *\
    def replace_clif_quotes (self):
        #print 'Replacing clif quotes and multiline comments'

        self.clif_processed_file_name = ColoreFileManager.get_name_with_subfolder(self.module_name, ColoreFileManager.GENERATED_FOLDER, LADR.PROVER9_ENDING + ClifModule.CLIF_ENDING)

        input_file = open(self.clif_file_name, 'r')
        output_file = open(self.clif_processed_file_name, 'w')
        line = input_file.readline()
        # currently within multiline comment section
        attribution_section = False
        while line:
            if attribution_section:
                if '*/' in line:
                    attribution_section = False
                    # normally process the remainder 
                    line = line.split('*/',1)
                    if len(line)>0:
                        line=line[1]
                else:
                    # if in multiline comment, ignore content
                    line = input_file.readline()
            elif '/*' in line:
                attribution_section = True
                line = line.split('/*',1)
                output_file.write(line[0])
                if len(line)>1:
                    line = line[1]
            else:
                output_file.write(line.replace('\"', '\''))
                line = input_file.readline()
        input_file.close()
        output_file.close()
        

    # extract all named entities (relations and functions) from a clif file
    def get_nonlogical_symbols (self):
        
        # get the named entities (functions and relations) from a string
        def get_logical_symbols_from_single_line(self, line):
            #print 'line: ' + line 
            
            s = line.find('(')
            while  s > -1:
                #print 'line before: ' + line
                line = line[s+1:]
                #print 'reduced line: ' + xline

                # we need the first closing parenthesis 
                e = line.find(')')
                
                if e<0:
                    # no closing parenthesis
                    activepart = line
                    line = ''
                else:
                    # find last  open parenthesis before the closing one
                    s2 = line.rfind('(', 0, e)
                    if s2<0:
                        # no other parenthesis
                        # split the line into an active parts that is immediately processed and the remainder of the line
                        activepart = line[0:e]
                        line = line[e+1:]
                    else:
                        activepart = line[s2+1:e]
                        line = line[0:s2] + ' ' + line[e+1:]
                        
                #print 'active part: ' + activepart
                
                if len(activepart)!=0:
                #print 'remainder of line: ' + line
                # split the active part into words
                    words = activepart.split()
                    
                    if words[0] in self.coloreprover.clif_logical_connectives:
                        # remove the connective, add the remainder to the remaining line
                        line = activepart[len(words[0]):] + line
                        #print 'line after processing connectives: ' + line
                    elif words[0] not in self.coloreprover.irrelevant_clif_symbols:
                        self.nonlogical_symbols.append(words[0])
                # next one 
                s = line.find('(')
    
    
        def get_quantified_variables_from_single_line (self,line):
            #print 'line (initial) = ' + line
            line = line.strip()
            #print 'all variables: ' + str(logical_vars)
            
            for keyword in self.coloreprover.quantifiers:
                i = line.find(keyword)
                while  i > -1:
                    #print 'line: ' + line
                    s = line.find('(',i)
                    e = line.find(')', s)
                    var_string = line[s+1:e]
                    remainder = line[e:]
                    #print 'logical_vars: ' + var_string
                    #print 'remainder: ' + remainder                   
                    for var in var_string.split():
                        if var not in self.nonlogical_variables:
                            #print 'new var: ' + var
                            self.nonlogical_variables.append(var)
                    line = remainder
                    i = line.find(keyword)
                
        def strip_comments (line):
            keyword = 'cl-comment'
            
            # remove trailing comments
            lineparts = line.strip().split('#')
            
            if not lineparts[0]:
                return ''
            
            line = lineparts[0]
            
            c1 = line.find(keyword)
            if c1>-1:
                s = line.find('\'',c1)
                e = line.find('\'',s+1)
                c2 = line.find(')',e+1)
                if s<0 or e<0 or c2<0:
                    return line[0:c1]
                
                #comment = line[c1:c2]
                #print 'comment: ' + comment
                line = line[0:c1] + line[c2:] 
                #print 'rest of line: ' + line
            return line
            

        cl_file = open(self.clif_processed_file_name, 'r')
        line = cl_file.readline()
        while line:
            # remove comments
            line = strip_comments(line)
            get_logical_symbols_from_single_line(self,line)
            get_quantified_variables_from_single_line(self,line)
            line = cl_file.readline()
            
        cl_file.close()
        
        
        #print 'all variables: ' + str(logical_vars) 
        #print 'all named entities : ' + str(namedentities)    
        
        
    # import a single module (resolve imports)
    def write_p9_file (self):
        # want to create a subfolder for the output files
        p9_file_name = self.p9_file_name
        
        if not self.clif:
            return self.p9_file_name
        else:
            p9_file = open(self.p9_file_name, 'w')
            p9i_file = open(self.p9_intermediary_file_name, 'r')
            line = p9i_file.readline()
            while line:
                keyword = 'imports('
                if line.strip().find(keyword) > -1:
                    #print 'module import found'
                    p9_file.write('%' + line)
                    new_module_name = line.strip()[len(keyword)+1:-3].strip()
                    self.coloreprover.append_module(new_module_name, self.depth+1)
                else:
                    p9_file.write(line)
                line = p9i_file.readline()
            p9i_file.close()
            p9_file.close()
        

    def get_p9_file_name (self):
        return ColoreFileManager.get_name_with_subfolder(self.module_name, LADR.P9_FOLDER, LADR.PROVER9_ENDING)
