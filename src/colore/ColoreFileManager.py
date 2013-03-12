'''
Created on 2011-04-29

@author: Torsten Hahmann
'''

import os
from LADR import LADR
from TPTP import TPTP

class ColoreFileManager(object):

    OUTPUT_FOLDER = 'output'
    
    # ending for all proof or consistency output
    OUTPUT_ENDING = '.out'

    GENERATED_FOLDER = 'generated'
           
    # determines the suitable subfolder for a given file_name
    @staticmethod
    def get_name_with_subfolder (complete_path_and_name, folder, ending=''):
        
        #print complete_path_and_name
            
        SUBFOLDERS = set([LADR.P9_FOLDER, TPTP.TPTP_FOLDER, ColoreFileManager.OUTPUT_FOLDER, ColoreFileManager.GENERATED_FOLDER])
            
        (dir, filename) = os.path.split(complete_path_and_name)
        if (len(dir)>0 and len(filename)>0):
            # strip other folder names:
            directory_parts = dir.rsplit(os.sep,1)
#            if len(directory_parts)==2:
#                print directory_parts[1]
            if len(directory_parts)==2:
                #directory_parts[1] = '/' + directory_parts[1]
                #print directory_parts[1]
                # remove special folder from path
                if directory_parts[1] in SUBFOLDERS:
                    dir = directory_parts[0]
#                else:
#                    print 'stripped subfolder ' + directory_parts[1] 
            directory = os.path.join(dir,folder)
            out_file_name = os.path.join(directory,filename + ending)
        else:
            directory = folder
            out_file_name = os.path.join(directory, filename + ending)
        # create the directory if necessary
        if not os.path.exists(directory):
            os.makedirs(directory)
        return out_file_name
    
    

    # take a lemma file in Prover9 and split it into individual Prover9 lemma files
    @staticmethod
    def get_individual_sentences(sentence_set_name, sentence_set_file):
        
        input_file = open(sentence_set_file, 'r')
        print 'sentences in : ' + sentence_set_file
        
        sentences = []
        imports = []
        
        # split the input file into several sentences
        line = input_file.readline()
        started = False
        while line:
            lineparts = line.strip().split('%')
            #print lineparts
            if lineparts[0]:
                if not started:
                    if line.find('formulas(sos).') > -1 or line.find('formulas(assumptions).') > -1:
                        started  = True
                else:
                    if line.find('end_of_list.') > -1:
                        break
                    else:
                        sentences.append(lineparts[0])
            elif len(lineparts)>=2 and lineparts[1].find('cl-imports')>-1:
                imports.append(line)
            line = input_file.readline()
        input_file.close()
    
    
        # write each lemma file
        sentences_names = []
        sentences_files = []
        i = 1
        for lemma in sentences:
            name = sentence_set_name + '_' + str(i)
            filename = ColoreFileManager.get_name_with_subfolder(name, LADR.P9_FOLDER, LADR.PROVER9_ENDING)
            output_file = open(filename, 'w')
            output_file.write('formulas(goals).\n')
            for single_import in imports:
                output_file.write(single_import)
            output_file.write(lemma + '\n')
            output_file.write('end_of_list.\n')
            output_file.close()
            sentences_names.append(name)
            sentences_files.append(filename)
            i += 1
        
        return sentences_names, sentences_files
        
