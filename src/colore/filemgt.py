'''
Created on 2011-04-29
Major revision (restructed as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os, filemgt
from ConfigParser import SafeConfigParser

CONFIG_PARSER = None
conf = None
config_file = 'macleod.conf'
config_dir = 'conf'

def find_config():
    """tries to find and then read the MacLeod configuration file."""
    file= filemgt.config_file
    for loc in os.path.curdir, os.path.join(os.path.curdir,filemgt.config_dir), os.path.expanduser("~"), os.environ.get("MACLEOD_CONF"):
        try:
            if not loc:
                loc = ""
            loc = os.path.join(loc,filemgt.config_file)
            print("Looking for Macleod configuration file at: " + loc)
            if os.path.isfile(loc):
                filemgt.config_file = loc
                print("Macleod configuration file found at: " + filemgt.config_file)
                filemgt.conf = filemgt.CONFIG_PARSER.read(config_file)
                break
        except IOError:
            pass


def read_config(section, key):
    """read a value from the MacLeod configuration file."""     
    # load 
    if not filemgt.CONFIG_PARSER:
        filemgt.CONFIG_PARSER = SafeConfigParser()
        filemgt.find_config()
        if len(conf)==0:
            print("Problem reading config file from " + os.path.abspath(os.path.curdir) + filemgt.config_file)
        
    # read from config
    return filemgt.CONFIG_PARSER.get(section,key)

        # test config parser
        #print(CONFIG_PARSER.get('converters', 'clif-to-prover9'))
     

  
def get_full_path (module_name, folder=None, ending=''):
    """determines the suitable subfolder for a given file_name."""
    path = filemgt.read_config('cl','path') + os.sep + module_name
    if folder:
        path = os.path.dirname(path) + os.sep + folder + os.sep + os.path.basename(path)
    # create this folder if it does not exist yet
    path = os.path.normpath(path)
    if not os.path.isdir(os.path.dirname(path)):
        if os.mkdir(os.path.dirname(path)):
            print "Created folder " + path
    
    return os.path.abspath(path + ending)


def get_tptp_symbols ():
    """get all options and their values from a section as a dictionary."""
    options = {}
    if not filemgt.CONFIG_PARSER:
        filemgt.CONFIG_PARSER = SafeConfigParser()
        filemgt.find_config()
    symbol_file = os.path.normpath(os.path.dirname(os.path.abspath(filemgt.config_file)) + os.sep + filemgt.read_config("converters","tptp_symbols"))
        
    file = open(symbol_file,"r")
    for line in file.readlines():
        if line.startswith('"'):
            line = line.strip('"').split('"')
            key = line[0].strip('"')
            value = line[1].strip().strip(':').strip()
            options[key] = value
        else:
            options[line.split(":")[0].strip()] = line.split(":")[1].strip()
    return options
    
        
