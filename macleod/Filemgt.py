'''
Created on 2011-04-29
Major revision (restructured as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

from pathlib import Path
from configparser import ConfigParser
import os, platform, logging, logging.config

#macleod_dir = os.path.realpath(__file__).rsplit(os.sep, 1)[0] + os.sep + '..'

WIN_config_file = 'macleod_win.conf'
LINUX_config_file = 'macleod_linux.conf'
MAC_config_file = 'macleod_mac.conf'


class MacleodConfigParser(object):

    __instance = None

    __config_dir = str(Path.home().joinpath('macleod'))
    __config_file = ''

    def __new__(cls):
        """ instantiating a single instance of a ConfigParser if it doesn't already exist"""
        if MacleodConfigParser.__instance is None:
            logging.getLogger(__name__).debug('Creating MacleodConfigParser')
            config_file = MacleodConfigParser.__config_dir

            if str(platform.system()) == 'Windows':
                config_file = os.path.join(config_file, WIN_config_file)
            elif str(platform.system()) == 'Darwin':
                config_file = os.path.join(config_file, MAC_config_file)
            else:
                config_file = os.path.join(config_file, LINUX_config_file)

            logging.getLogger(__name__).info('config file found: ' + str(config_file))
            MacleodConfigParser.__config_file = os.path.abspath(config_file)
            MacleodConfigParser.__instance = ConfigParser()
            MacleodConfigParser.__instance.read(MacleodConfigParser.__config_file)

        else:
            logging.getLogger(__name__).debug('Existing MacleodConfigParser')
        return MacleodConfigParser.__instance

    def find_config (filename):
        """tries to find some configuration file with the path filename."""
        print("Trying to find config file " + filename)
        try:
            logging.getLogger(__name__).debug("Looking for " + filename + " at: " + os.path.curdir)
            filename = os.path.normpath(os.path.join(os.path.abspath(os.path.curdir), filename))
            if os.path.isfile(filename):
                logging.getLogger(__name__).debug(filename + " FOUND")
        except IOError:
            pass
        return filename

    def get(self,section, key):
        return __instance.get(section, key)


def read_config(section, key, file=None):
    from configparser import NoOptionError

    """read a value from the MacLeod configuration file."""
    if file is None:
        try:
            return MacleodConfigParser().get(section, key)
        except NoOptionError as e:
            logging.getLogger(__name__).warn('COULD NOT FIND OPTION: ' + key + ' in section ' + section)
    else:
        CONFIG_PARSER_TEMP = ConfigParser()
        if os.path.isfile(file):
            CONFIG_PARSER_TEMP.read(file)
            try:
                return CONFIG_PARSER_TEMP.get(section,key)
            except NoOptionError as e:
                logging.getLogger(__name__).warn('COULD NOT FIND OPTION: ' + key + ' in section ' + section)
    return None


def edit_config(section, key, value, file):
    CONFIG_PARSER_TEMP = SafeConfigParser()
    CONFIG_PARSER_TEMP.read(file)
    CONFIG_PARSER_TEMP.set(section,key, value)

    if os.path.isfile(file):
        with open(file,'w') as cfgfile:
            CONFIG_PARSER_TEMP.write(cfgfile)


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
                logging.getLogger(__name__).info('CREATED FOLDER: ' + path)
            except OSError as e:
                logging.getLogger(__name__).warn('COULD NOT CREATE FOLDER: ' + path + ' Error: ' + str(e))

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
    """get all options and their values from a section as a dictionary."""
    options = {}
    symbol_file_name = os.path.normpath(os.path.dirname(os.path.abspath(MacleodConfigParser.__config_file)) + os.sep + read_config("converters","tptp_symbols"))

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
