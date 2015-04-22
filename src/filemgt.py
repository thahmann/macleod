'''
Created on 2011-04-29
Major revision (restructured as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os, logging.config
from ConfigParser import SafeConfigParser

LOGGER = None
CONFIG_PARSER = None
log_config_file = '../conf/logging.conf'
#config_file = '../conf/macleod_mac.conf'
config_file = 'macleod.conf'
config_dir = '../conf/'

subprocess_log_file = None


def find_config (filename):
    """tries to find some configuration file."""
    for loc in os.path.curdir, os.path.join(os.path.curdir,config_dir), os.path.join(os.path.curdir,config_dir), os.path.join(os.path.curdir,'..',config_dir), os.path.expanduser("~"), os.environ.get("MACLEOD_CONF"):
        try:
            if not loc:
                loc = ""
            loc = os.path.join(loc,filename)
            if LOGGER:
                LOGGER.debug("Looking for " + filename + " at: " + loc)
            else:
             print("Looking for configuration file at: " + loc)
            if os.path.isfile(loc):
                filename = loc
                if LOGGER:
                    LOGGER.debug(filename + " FOUND")
                else:
                    print("File " + filename + " found")
                break
        except IOError:
            pass
    if len(filename)>0:
        filename = os.path.normpath(os.path.join(os.path.abspath(os.path.curdir), filename))
    return filename


def find_macleod_config():
    """tries to find the MacLeod configuration file."""
    global config_file
    filename = config_file
    config_file = filename

    if not os.path.exists(config_file) or not os.path.isfile(config_file):
        # backup solution: with _win or _linux in the name
        basename = os.path.basename(filename).rsplit(".",1)
        if len(basename)==2:
            new_basename = basename[0]
            if os.name == 'nt':
                new_basename += "_win"
	    elif (os.name == 'posix'):
		new_basename += "_mac"
            else:
                new_basename += "_linux"
            new_basename += "." + basename[1]
            filename = os.path.join(os.path.dirname(filename), new_basename)
            config_file = find_config(filename)


def find_log_config():
    global log_config_file
    """tries to find the MacLeod logging configuration file."""
    #log_config_file = find_config(log_config_file)
    #print("Log config file found: " + log_config_file)
         

def read_config(section, key):
    """read a value from the MacLeod configuration file."""
    # load
    global CONFIG_PARSER
    global LOGGER
    if not CONFIG_PARSER:
        CONFIG_PARSER = SafeConfigParser()
        find_macleod_config()
        if len(config_file)==0:
            LOGGER.error("Problem reading config file from " + config_file)
        else:
            #print("Read config file from " + config_file)
            CONFIG_PARSER.read(config_file)
            LOGGER.info('Macleod configuration read from ' + config_file)
        
    # read from config
    return CONFIG_PARSER.get(section,key)
     
def start_logging():
    """create a MacLeod logger and start logging."""
    global LOGGER
    if not LOGGER:
        find_log_config()
        if len(log_config_file)==0:
            print("Problem reading logging config file from " + log_config_file)
        else:
            print("Read logging config file from " + log_config_file)
            logging.config.fileConfig(log_config_file)
            # create logger
            LOGGER = logging.getLogger(__name__)
            LOGGER.debug('Logging started')
            LOGGER.debug('Logging configuration read from ' + log_config_file)


def find_subprocess_log_file():
    global subprocess_log_file
    if not subprocess_log_file:
        find_log_config()
        SafeConfigParser().read(log_config_file)
        subprocess_log_file = read_config("system","subprocess_log")

    
def add_to_subprocess_log(entries):
    global LOGGER
    find_subprocess_log_file()
    LOGGER.debug("Writing " + str(len(entries)) + " lines to subprocess log file " + subprocess_log_file)
    if os.path.exists(subprocess_log_file):
        sp_log_file = open(subprocess_log_file, 'a')
    else:
        sp_log_file = open(subprocess_log_file, 'w')
    #for e in entries:
    # LOGGER.info("____WRITING " + e)
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
            except OSError, e:
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

    
def	get_hierarchy_name (module_name):
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
    if not CONFIG_PARSER:
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
    
