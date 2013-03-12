'''
Created on 2010-11-26

@author: Torsten Hahmann
'''
import os, subprocess, time
from Process import Process

class LADR(object):

    # locations of mace4 and prover9 (comes with Prover9-Mace4)
    # here it is simply assumed they are in the PATH
    MACE4 = 'mace4'
    PROVER9 = 'prover9'

    P9_FOLDER = 'p9'
        
    PROVER9_ENDING = '.p9'
    MACE4_ENDING = '.m4'

    # option file for Prover9 containing, e.g., predicate orderings
    P9_OPTIONS_FILE_NAME = 'options.txt'


    ## options for Prover9 and Mace4
    max_seconds_proof = 0
    max_seconds_counter = 0
    max_seconds_counter_per = 0
    start_size = 0
    end_size = 0    

    options_files = []

    def __init__(self):
        self.max_seconds_proof = 600
        self.max_seconds_counter = 600
        self.max_seconds_counter_per = 60
        self.start_size = 2
        self.end_size = 20    
        

    # run prover9 and mace4 in parallel
    @staticmethod
    def run_p9_and_m4(p9cmd, m4cmd):
            
    
        time.sleep(1.0)
    
        p9 = subprocess.Popen(p9cmd, shell=True, close_fds=True, preexec_fn=os.setsid)
        m4 = subprocess.Popen(m4cmd, shell=True, close_fds=True, preexec_fn=os.setsid)
        
        while p9.returncode is None and m4.returncode is None:
            time.sleep(2.0)
            p9.poll()
            m4.poll()
        
        while p9.returncode is None or m4.returncode is None:
            # do not check for Exit Code 2 in Mace4: could quickly run through the domain sizes without giving Prover9 enough time to find a proof
            # exit codes 0, 3, 4 indicate that a model was found 
            if m4.returncode in [0,3,4,101,102] and p9.returncode is None:
                Process.terminate(p9)
                p9.wait()
                #filename = r'%s' % (p9out)
                #os.remove(filename)
            # do not check for Exit Code 2 in Prover9: merely says SOS was empty, Mace4 could still find a counterexample
            if p9.returncode in [0,101,102] and m4.returncode is None:
                Process.terminate(m4)
                m4.wait()
                #filename = r'%s' % (m4out) 
                #os.remove(filename)
            time.sleep(2.0)
            p9.poll()
            m4.poll()
        
        # just sort the output
        time.sleep(1.0)
        
        return (p9.returncode, m4.returncode) 
    
    
    # get a formatted command to run Prover9 with options (timeout, etc.) set in the class instance
    def get_p9_basic_cmd (self,imports):
        
        prover9args = LADR.PROVER9
        
        if self.max_seconds_proof:
            prover9args += ' -t ' + repr(self.max_seconds_proof)
        
        prover9args += ' -f '
        for m in imports:
            prover9args += m.p9_file_name + ' '
        if LADR.options_files:
            for f in LADR.options_files:
                prover9args += f + ' '
    
        return prover9args
        
    
    # get a formatted command to run Mace4 with options (timeout, etc.) set in the class instance
    def get_m4_basic_cmd (self,imports):
    
        mace4args = LADR.MACE4 + ' -c '
        
        if self.max_seconds_counter:
            mace4args += ' -t ' + repr(self.max_seconds_counter)
        if self.max_seconds_counter_per:
            mace4args += ' -s ' + repr(self.max_seconds_counter_per)
        if self.start_size:
            mace4args += ' -n ' + repr(self.start_size)
        if self.end_size:
            mace4args += ' -N ' + repr(self.end_size)
        
        mace4args += ' -f '
        for m in imports:
            mace4args += m.p9_file_name + ' '
#        if self.options_files:
#            for f in self.options_files:
#                mace4args += f + ' '
        
        return mace4args
    
    
    # generate an options file for prover9
    @staticmethod
    def get_p9_optionsfile (p9_file_name, verbose=True):
    
        # currently one option file for all!!
        #print 'OPTIONS FILE - P9 file name = ' + p9_file_name
        options_file_name = os.path.join(os.path.dirname(p9_file_name), LADR.P9_OPTIONS_FILE_NAME)
        
        #print 'OPTIONS FILE = ' + options_file_name
    
        LADR.options_files.append(options_file_name)
    
        if os.path.isfile(options_file_name):
            return options_file_name
        else:
        #    options_file_name = module_p9_file + '.options'
            options_file = open(options_file_name, 'w')
            options_file.write('clear(auto_denials).\n')
            if not verbose:
                options_file.write('clear(print_initial_clauses).\n')
                options_file.write('clear(print_kept).\n')
                options_file.write('clear(print_given).\n')
                #options_file.write('set(quiet).')
            options_file.close()
            return options_file_name
    
    
    # delete all option files and empty the list of option files
    @staticmethod
    def cleanup_option_files():
        for m in LADR.options_files:
            if os.path.exists(m):
                os.remove(m)
        LADR.options_files = []
        
        
     
    # puts a set of p9 files into a single file while converting all uppercase letters to lowercase (only the filename, not the entire path!)
    @staticmethod
    def get_single_lowercase_p9file (imports, output_file, special_symbols):    
        LADR.cumulate_p9files(imports, output_file, special_symbols)

        out_file = open(output_file, 'r+')
        old = out_file.read() # read everything in the file
        out_file.seek(0) # rewind
        # only conert the actual filename to lowercase
        new = os.path.join(os.path.dirname(old), os.path.basename(old).lower())
        out_file.write(new) # write the new line        
        #print new
        out_file.close()

    # write all axioms from a set of p9 files to a single file and reduce it to a single block of axioms 
    @staticmethod
    def get_single_p9file(imports,output_file, special_symbols):
        LADR.cumulate_p9files(imports, output_file, special_symbols)

        old_file = open(output_file,'r')
        old = old_file.read()  # read everything in the file
        old_file.close()

        new = LADR.strip_inner_p9commands(old)

        out_file = open(output_file, 'w')
        out_file.write(new) # write the new line        
        out_file.close()
        
    
    # write all axioms from a set of p9 files to a single file without any change in the content itself
    @staticmethod
    def cumulate_p9files (imports, output_file, special_symbols):    
    
        out_file = open(output_file, 'w')
        for f in imports:
            in_file = open(f, 'r')
            line = in_file.readline()
            out_file.write('%axioms from module ' + f + '\n')
            out_file.write('%----------------------------------\n')
            out_file.write('\n')
            while line:
                if special_symbols:
                    for (key, replacement) in special_symbols:
                        line = line.replace(' '+key+'(', ' '+replacement+'(')
                        line = line.replace('('+key+'(', '('+replacement+'(')
                out_file.write(line)
                line = in_file.readline()
            out_file.write('\n') 
            in_file.close()
        
        
        
        out_file.close()
        return output_file
        
    # remove all "formulas(sos)." and "end_of_list." from a p9 file assembled from multiple axiom files; leaving a single block of axioms
    @staticmethod
    def strip_inner_p9commands(text):
        parts = text.split('formulas(sos).\n',1)
        text = parts[0] +'formulas(sos).\n' + parts[1].replace('formulas(sos).\n','')
        i = text.count('end_of_list.\n')
        text = text.replace('end_of_list.\n','',i-1)
        return text
