'''
Created on 2011-04-29
Major revision (restructured as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

from pathlib import Path
import os, platform, logging.config
from configparser import SafeConfigParser

LOGGER = None
CONFIG_PARSER = None
macleod_dir = os.path.realpath(__file__).rsplit(os.sep, 1)[0] + os.sep + '..' 

log_config_file_name = 'logging.conf'
log_config_file = None

WIN_config_file = 'macleod_win.conf'
LINUX_config_file = 'macleod_linux.conf'
MAC_config_file = 'macleod_mac.conf'

config_dir = str(Path.home().joinpath('macleod'))
config_file = ''

log_dir = None
log_file = None
subprocess_log_file = None

def find_config (filename):
    """tries to find some configuration file with the path filename."""
    print("Trying to find config file " + filename)
    try:
        if LOGGER:
            LOGGER.debug("Looking for " + filename + " at: " + os.path.curdir)
        else:
            print(("Looking for configuration file at: " + os.path.curdir))
        filename = os.path.normpath(os.path.join(os.path.abspath(os.path.curdir), filename))
        if os.path.isfile(filename):
            if LOGGER:
                LOGGER.debug(filename + " FOUND")
            else:
                print(("File " + filename + " found"))
    except IOError:
        pass
    return filename


def find_macleod_config():
    """tries to find the Macleod configuration file."""
    global config_file
    #config_file = macleod_dir
    config_file = config_dir
    if str(platform.system()) == 'Windows':
        config_file = os.path.join(config_file, WIN_config_file)
    elif str(platform.system()) == 'Darwin':
        config_file = os.path.join(config_file, MAC_config_file)
    else:
        config_file = os.path.join(config_file, LINUX_config_file)

    config_file = find_config(os.path.abspath(config_file))


def find_log_config():
    """tries to find the MacLeod logging configuration file."""
    global log_config_file
    log_config_file = config_dir + os.sep + log_config_file_name
    log_config_file = find_config(os.path.abspath(log_config_file))
    print(("Log config file found: " + log_config_file))

def create_log_file_path():
    import errno
    global log_dir
    global log_file
    global subprocess_log_fiel
    log_dir = read_config("logging","logdir")
    # ensure that the directory for the logging file exists
    try:
        os.makedirs(log_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(log_dir):
            pass
        else: raise
    # read names of logging files
    log_file = read_config("logging","logfile")
    subprocess_log_file = read_config("logging","subprocess_logfile")
    # create the complete path for the the log file and the subprocess log file
    log_file = os.path.normpath(os.path.join(os.path.abspath(log_dir), log_file))
    subprocess_log_file = os.path.normpath(os.path.join(os.path.abspath(log_dir), subprocess_log_file))
    # write global log file name to logging configuration
    args_string = read_config("handler_fHandler","args",log_config_file)
    print("OLD ARGS = " + args_string)
    # strings outer parentheses
    args_string = args_string[1:-1]
    # strips all quotation marks
    args_string = args_string.replace("'","")
    args_string = args_string.replace('"','')
    args = args_string.split(",")
    print(args)
    # filter empty strings from list of args
    args = [_f for _f in args if _f]
    # normalize all paths to which the logger is supposed to write
    args = [os.path.normpath(os.path.abspath(a)) for a in args]
    args = [a for a in args if os.path.isfile(a)]
    print("CHECKING FOR " + log_file + " IN ARGS")
    if not log_file in args:
        args.append(log_file)
        print(args)
        args_string = "("
        for a in args:
            args_string += "'" + a + "',"
        args_string += ")"
        print("NEW ARGS = " + args_string)
        edit_config("handler_fHandler","args",args_string,log_config_file)


def read_config(section, key, file=None):
    """read a value from the MacLeod configuration file."""
    global CONFIG_PARSER

    if file is None:
        if CONFIG_PARSER is None:
            print("CONFIG_PARSER missing") 
            CONFIG_PARSER = SafeConfigParser()
            find_macleod_config()
        if len(config_file)>0:
            #print("Read config file from " + config_file)
            CONFIG_PARSER.read(config_file)
            #LOGGER.info('Macleod configuration read from ' + config_file)
            return CONFIG_PARSER.get(section,key)
    else:
        CONFIG_PARSER_TEMP = SafeConfigParser()
        if os.path.isfile(file):
            CONFIG_PARSER_TEMP.read(file)
            return CONFIG_PARSER_TEMP.get(section, key)
    return None


def edit_config(section, key, value, file):
    CONFIG_PARSER_TEMP = SafeConfigParser()
    CONFIG_PARSER_TEMP.read(file)
    CONFIG_PARSER_TEMP.set(section,key, value)

    if os.path.isfile(file):
        with open(file,'w') as cfgfile:
            CONFIG_PARSER_TEMP.write(cfgfile)


def start_logging():
    """create a MacLeod logger and start logging."""
    global long_config_file
    global LOGGER
    if not LOGGER:
        find_log_config()
        create_log_file_path()
        if len(log_config_file)==0:
            print(("Problem reading logging config file from " + log_config_file))
        else:
            print(("Read logging config file from " + log_config_file))
            create_log_file_path()	
            LOGGER = logging.getLogger(__name__)
            LOGGER.debug('Logging started')
            LOGGER.debug('Logging configuration read from ' + log_config_file)

def find_subprocess_log_file():
    global log_dir
    global subprocess_log_file
    if not subprocess_log_file:
        find_log_config()
        SafeConfigParser().read(log_config_file)
        filename = read_config("logging","subprocess_logfile")
        subprocess_log_file = os.path.normpath(os.path.join(os.path.abspath(log_dir), filename))


def add_to_subprocess_log(entries):
    global LOGGER
    global subprocess_log_file
    find_subprocess_log_file()
    LOGGER.debug("Writing " + str(len(entries)) + " lines to subprocess log file " + subprocess_log_file)
    if os.path.exists(subprocess_log_file):
        sp_log_file = open(subprocess_log_file, 'a')
    else:
        sp_log_file = open(subprocess_log_file, 'w')

    sp_log_file.writelines([e + "\n" for e in entries])
    sp_log_file.close()
    return True


def format(record):
    formatter = logging.Formatter("%(asctime)s %(name)-30s %(levelname)-8s %(message)s")
    return formatter.format(record)

def get_full_path (module_name, folder=None, ending=''):
    """determines the suitable subfolder for a given file_name."""
    module_name = os.path.normpath(module_name)
    if os.sep in module_name:
        #print "Getting path for: " + module_name
        path = module_name.rsplit(os.sep,1)
        module_name = path[1]
        path = path[0]
        path = os.path.abspath(os.path.join(read_config('system','path'), path))
        if folder:
            path = os.path.abspath(os.path.join(path, folder))
            # create this folder if it does not exist yet
        if not os.path.exists(path):
            try:
                os.mkdir(path)
                LOGGER.info('CREATED FOLDER: ' + path)
            except OSError as e:
                LOGGER.warn('COULD NOT CREATE FOLDER: ' + path + ' Error: ' + str(e))

        if module_name.endswith(ending):
            return os.path.abspath(os.path.join(path, module_name))
        else:
            return os.path.abspath(os.path.join(path, module_name + ending))
    else:
        if folder:
            path = os.path.abspath(os.path.join(read_config('system','path'), folder))
        else:
            path = os.path.abspath(read_config('system','path'))

        return os.path.abspath(os.path.join(path, module_name + ending))

def get_canonical_relative_path (path):
    """determines the path of a module relative to the path specified in the configuration"""
    #print "Getting canonical path for: " + path
    abspath = os.path.abspath(path)
    abspath = abspath.split(read_config('system','path') + os.sep,1)
    if len(abspath)>1: # if the absolute path contains on
        path = abspath[1]
    else:
        # if the path does not contain the system-configured path, keep the original name, but remove standard prefixes
        import re
        prefix = read_config('cl','prefix')
        if path.startswith(prefix):
            path = path.replace(prefix,'',1)
    if path.endswith(read_config('cl','ending')):
        path = path.rsplit(read_config('cl','ending'),1)[0]
    return os.path.normcase(path)


def get_path_with_ending_for_nontrivial_consistency_checks (module_name):
    """determines and returns the path of the module that checks for nontrivial consistency of the module named module_name.""" 
    subfolder=read_config('cl','consistency_subfolder')
    if module_is_definition_set(module_name):
        module_name = "".join(module_name.rsplit(read_config('cl','definitions_subfolder')+os.sep,1))
    path = get_full_path(module_name + '_nontrivial', subfolder, read_config('cl','ending'))
    #print "PATH FOR CONSISTENCY CHECK of " + module_name + ": " + path
    consistency_module_name = get_canonical_relative_path(path) + read_config('cl','ending')
    #print "CANONICAL PATH FOR CONSISTENCY CHECK of " + module_name + ": " + path
    return_value = (consistency_module_name, path)
    #print return_value 
    return return_value

def get_hierarchy_name (module_name):
    """determines the part of the module_name that denotes the hierarchy."""
    module_name = os.path.normcase(module_name)
    if os.sep in module_name:
        path = module_name.rsplit(os.sep,1)[0]
        sentence_type = get_type(module_name)
        if type=="":
            return path
        else:
            return path.rsplit(os.sep + sentence_type)[0]
    else:
        return ""

def get_type (module_name):
    """determines whether this is a axiom, definition, mapping, theorem, etc. file"""
    module_name = os.path.normcase(module_name)
    if os.sep in module_name:
        path = module_name.rsplit(os.sep,1)[0]
        if os.sep in path:
            subfolder = path.rsplit(os.sep,1)[1]
            #print "SUBFOLDER = " + subfolder
            if (subfolder==read_config('cl','definitions_subfolder')): 
                return read_config('cl','definitions_subfolder')
            elif (subfolder==read_config('cl','theorems_subfolder')): 
                return read_config('cl','theorems_subfolder')
            elif (subfolder==read_config('cl','consistency_subfolder')): 
                return read_config('cl','consistency_subfolder')
            elif (subfolder==read_config('cl','interpretations_subfolder')): 
                return read_config('cl','interpretations_subfolder')
            elif (subfolder==read_config('cl','mappings_subfolder')): 
                return read_config('cl','mappings_subfolder')
            # TODO: complete folders as necessary
    return ""

def module_is_axiom_set (module_name):
    if get_type(module_name)=="":
        return True
    else:
        return False

def module_is_definition_set (module_name):
    if get_type(module_name)==read_config('cl','definitions_subfolder'):
        #print "FOUND DEFINITION: " + module_name
        return True
    else:
        return False


def module_is_theorem_set (module_name):
    if get_type(module_name)==read_config('cl','theorems_subfolder'):
        return True
    else:
        return False


def get_tptp_symbols ():
    global CONFIG_PARSER
    """get all options and their values from a section as a dictionary."""
    options = {}
    if CONFIG_PARSER is None:
        CONFIG_PARSER = SafeConfigParser()
        find_config()
    symbol_file_name = os.path.normpath(os.path.dirname(os.path.abspath(config_file)) + os.sep + read_config("converters","tptp_symbols"))

    symbol_file = open(symbol_file_name,"r")
    for line in symbol_file.readlines():
        if line.startswith('"'):
            line = line.strip('"').split('"')
            key = line[0].strip('"')
            value = line[1].strip().strip(':').strip()
            options[key] = value
        else:
            options[line.split(":")[0].strip()] = line.split(":")[1].strip()
    return options
