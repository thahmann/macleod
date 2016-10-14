'''
Created on 2010-11-26

@author: Torsten Hahmann
'''
import macleod.Filemgt as filemgt
import macleod.Ladr as ladr
import os, logging

options_files = []


def get_system_command(system_name, imports, output_stem):
    """chooses the correct constructor that sets the command up depending on the selected system"""
    handlers = {
        "prover9": get_p9_cmd, 
        "mace4":  get_m4_cmd,
        "paradox": get_paradox_cmd,
        "vampire": get_vampire_cmd
    }

    logging.getLogger(__name__).debug("CONSTRUCTING COMMAND FOR: " + system_name + " FROM " + str(imports))

    return handlers.get(system_name, get_empty_cmd)(imports,output_stem)


def get_positive_returncodes (name):
    return get_returncodes(name)

def get_unknown_returncodes (name):
    return get_returncodes(name, type="unknown_returncode")

def get_returncodes (name,type="positive_returncode"):
    code_list = filemgt.read_config(name,type) 
    codes = []
    if len(code_list)>0:
        codes = [ int(s.strip()) for s in code_list.split(',')]
    return codes


def get_empty_cmd():
    return ""

def get_p9_cmd (imports,output_stem, option_files = None):
    """get a formatted command to run Prover9 with options (timeout, etc.) set in the class instance."""

    args = []
    args.append(filemgt.read_config('prover9','command'))
    args.append('-t' + filemgt.read_config('prover9','timeout'))
    args.append('-f')
    # append all ladr input files
    for m in imports:
        args.append(m.get_p9_file_name())
    if option_files:
        for f in option_files:
            args.append(f)

    return (args, [])


def get_m4_cmd (imports,output_stem):
    """get a formatted command to run Mace4 with options (timeout, etc.) set in the class instance."""

    args = []
    args.append(filemgt.read_config('mace4','command'))
    args.append('-v0')
    args.append('-t' + filemgt.read_config('mace4','timeout'))
    args.append('-s' + filemgt.read_config('mace4','timeout_per'))
    args.append('-n' + filemgt.read_config('mace4','start_size'))
    args.append('-N' + filemgt.read_config('mace4','end_size'))
    args.append('-f')
    # append all ladr input files
    for m in imports:
        args.append(m.get_p9_file_name())

    return (args, [])


def get_paradox_cmd (imports,output_stem):
    """ we only care about the first element in the list of imports, which will we use as base name to obtain a single tptp file of the imports,
    which is the input for paradox."""
    args = []
    args.append(filemgt.read_config('paradox','command'))
    args.append('--time')
    args.append(filemgt.read_config('paradox','timeout'))
    args.append('--verbose')
    args.append('2')
    args.append('--model')
    args.append('--tstp')
    # append all tptp input files
    args.append(list(imports)[0].get_module_set(imports).get_single_tptp_file(imports))

    return (args, [])


def get_vampire_cmd (imports,ouput_stem):
    args = []
    args.append(filemgt.read_config('vampire','command'))
    args.append('--mode')
    args.append('casc')
    args.append('--proof')
    args.append('tptp')
    args.append('-t')
    args.append(filemgt.read_config('vampire','timeout'))
    # needed for Windows
    args.append('--input_file')
    args.append(list(imports)[0].get_module_set(imports).get_single_tptp_file(imports))
    logging.getLogger(__name__).debug("COMMAND FOR vampire IS " + str(args))
    # works for linux, not for Windows
    #return (args, [list(imports)[0].get_module_set(imports).get_single_tptp_file(imports)])

    return (args, [])



def get_ladr_to_tptp_cmd (input_file_name, output_file_name):
    cmd = filemgt.read_config('converters','prover9-to-tptp') + ' < ' + input_file_name + ' > ' + output_file_name
    return cmd




#-------------------------------
#---Clean up below--------------
#-------------------------------



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

