'''
Created on 2010-11-26

@author: Torsten Hahmann
'''
import os, subprocess, time, process, filemgt, commands

options_files = []


def get_system_command(system_name, imports, output_stem):
    """chooses the correct constructor that sets the command up depending on the selected system"""
    handlers = {
        "prover9": get_p9_cmd, 
        "mace4":  get_m4_cmd,
        "paradox": get_paradox_cmd,
        "vampire": get_vampire_cmd
    }

    return handlers.get(system_name, get_empty_cmd)(imports,output_stem)


def get_positive_returncodes (name):
    return commands.get_returncodes(name)

def get_unknown_returncodes (name):
    return commands.get_returncodes(name, type="unknown_returncode")
    
def get_returncodes (name,type="positive_returncode"):
    codes = filemgt.read_config(name,type).split(',')
    codes = [ int(s.strip()) for s in codes ]
    return codes


def get_empty_cmd():
    return ""

# get a formatted command to run Prover9 with options (timeout, etc.) set in the class instance
def get_p9_cmd (imports,output_stem, option_files = None):
    
    cmd = (filemgt.read_config('prover9','command') +
                ' -t ' + filemgt.read_config('prover9','timeout') +
                ' -f ')
    # append all ladr input files       
    for m in imports:
        cmd += m.get_p9_file_name() + ' '
    if option_files:
        for f in option_files:
            cmd += f + ' '

    return cmd + ' > ' + output_stem + filemgt.read_config('prover9','ending')
    

# get a formatted command to run Mace4 with options (timeout, etc.) set in the class instance
def get_m4_cmd (imports,output_stem):

    cmd = (filemgt.read_config('mace4','command') + ' -c ' +
                ' -t ' + filemgt.read_config('mace4','timeout') +
                ' -s ' + filemgt.read_config('mace4','timeout_per') +
                ' -n ' + filemgt.read_config('mace4','start_size') +
                ' -N ' + filemgt.read_config('mace4','end_size') +
                ' -f ')
    # append all ladr input files
    for m in imports:
        cmd += m.p9_file_name + ' '
#        if self.options_files:
#            for f in self.options_files:
#                mace4args += f + ' '
    
    return cmd + ' > ' + output_stem + filemgt.read_config('mace4','ending')


def get_paradox_cmd (imports,ouput_stem):
    cmd = (filemgt.read_config('paradox','command') +
                  ' --verbose 2 --model --tstp ' +
                  imports[0].tptp_file_name)
        
    return cmd + ' > ' + output_stem + filemgt.read_config('paradox','ending')


def get_vampire_cmd (imports,ouput_stem):
    cmd = (filemgt.read_config('vampire','command') + 
             ' --mode casc --proof tptp' +
             ' -t ' + repr(filemgt.read_config('vampire','timeout')) +
             ' < ' + m.tptp_file_name)

    return cmd + ' > ' + output_stem + filemgt.read_config('vampire','ending')


def get_clif_to_ladr_cmd (module):
    cmd = (filemgt.read_config('converters','clif-to-prover9') + ' ' + 
            module.clif_processed_file_name + ' > ' + 
            module.p9_file_name)
    return cmd


def get_ladr_to_tptp_cmd (input_file_name, output_file_name):
    cmd = filemgt.read_config('converters','prover9-to-tptp') + ' < ' + input_file_name + ' > ' + output_file_name
    return cmd


#-------------------------------
#---Clean up below--------------
#-------------------------------

# take a lemma file in the LADR format and split it into individual goals that can be feed into Prover9
def get_individual_p9_sentences(sentence_set_name, sentence_set_file):
    
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
        filename = ColoreFileManager.get_name_with_subfolder(name, 
                                                             filemgt.read_config('ladr','p9'), 
                                                             filemgt.read_config('ladr','ending'))
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


def cleanup_option_files():
    for m in LADR.options_files:
        if os.path.exists(m):
            os.remove(m)
    LADR.options_files = []

# generate an options file for prover9
def get_p9_empty_optionsfile (p9_file_name, verbose=True):

    # currently one option file for all!!
    #print 'OPTIONS FILE - P9 file name = ' + p9_file_name
    options_file_name = os.path.join(os.path.dirname(p9_file_name), 
                                     os.path.splitext(os.path.basename(p9_file_name))[0] + filemgt.read_config('prover9','options_ending'))
    
    #print 'OPTIONS FILE = ' + options_file_name

    ladr.options_files.append(options_file_name)

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

