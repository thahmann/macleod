'''
Created on 2010-11-26

@author: Torsten Hahmann
'''
import macleod.Ontology as Ontology
import macleod.Filemgt as filemgt
import macleod.Ladr as ladr
import os, logging


options_files = []


def get_system_command(system_name, ontology):
    """chooses the correct constructor that sets the command up depending on the selected system"""
    handlers = {
        "prover9": get_p9_cmd, 
        "mace4":  get_m4_cmd,
        "paradox": get_paradox_cmd,
        "vampire": get_vampire_cmd
    }

    logging.getLogger(__name__).debug("CONSTRUCTING COMMAND FOR: " + system_name + " FROM " + ontology.name)

    return handlers.get(system_name, get_empty_cmd)(ontology)


def get_empty_cmd():
    return ""

def get_p9_cmd (ontology):
    """get a formatted command to run Prover9 with options (timeout, etc.) set in the class instance."""

    args = []
    args.append(filemgt.read_config('prover9','command'))
    args.append('-t' + filemgt.read_config('prover9','timeout'))
    args.append('-f')
    args.append(ontology.write_ladr_file())

    # check for possible options file (to change predicate order or other parameters)
    options_file = filemgt.read_config('prover9', 'options')

    if options_file is not None:
        options_file = os.path.abspath(options_file)
        args.append(options_file)

    return args


def get_m4_cmd (ontology):
    """get a formatted command to run Mace4 with options (timeout, etc.) set in the class instance."""

    args = []
    args.append(filemgt.read_config('mace4','command'))
    args.append('-v0')
    args.append('-t' + filemgt.read_config('mace4','timeout'))
    args.append('-s' + filemgt.read_config('mace4','timeout_per'))
    args.append('-n' + filemgt.read_config('mace4','start_size'))
    args.append('-N' + filemgt.read_config('mace4','end_size'))
    args.append('-f')
    args.append(ontology.write_ladr_file())

    return args


def get_paradox_cmd (ontology):
    """ we only care about the first element in the list of imports, which will we use as base name to obtain a single tptp file of the imports,
    which is the input for paradox."""
    args = []
    args.append(filemgt.read_config('paradox','command'))
    # this option is needed for linux or mac to run paradox using wine, where "wine" is the command, but the path to paradox is the first argument, stored in the key "options"
    option = filemgt.read_config('paradox','options')
    if option is not None:
        args.append(option)
    args.append('--time')
    args.append(filemgt.read_config('paradox','timeout'))
    args.append('--verbose')
    args.append('2')
    args.append('--model')
    args.append('--tstp')
    args.append(ontology.write_tptp_file())

    return args


def get_vampire_cmd (ontology):
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
    args.append(ontology.write_tptp_file())
    #logging.getLogger(__name__).debug("COMMAND FOR vampire IS " + str(args))
    # works for linux, not for Windows
    #return (args, [list(imports)[0].get_module_set(imports).get_single_tptp_file(imports)])

    return args



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

