'''
Created on 2011-04-29
Major revision (restructed as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os, filemgt, logging, logging.config
from ConfigParser import SafeConfigParser

LOGGER = None
CONFIG_PARSER = None
log_config_file = 'logging.conf'
config_file = 'macleod.conf'
config_dir = 'conf'

def find_config (filename):
    """tries to find some configuration file."""
    for loc in os.path.curdir, os.path.join(os.path.curdir,filemgt.config_dir), os.path.expanduser("~"), os.environ.get("MACLEOD_CONF"):
        try:
            if not loc:
                loc = ""
            loc = os.path.join(loc,filename)
            if filemgt.LOGGER: 
                filemgt.LOGGER.debug("Looking for configuration file at: " + loc)
            #else:
            #    print("Looking for configuration file at: " + loc)
            if os.path.isfile(loc):
                filename = loc
                if filemgt.LOGGER: 
                    filemgt.LOGGER.debug("Configuration file found at: " + filename)
                else:
                    print("Configuration file found at: " + filename)
                break
        except IOError:
            pass
    if len(filename)>0:
        filename = os.path.normpath(os.path.join(os.path.abspath(os.path.curdir), filename))
    return filename

def find_macleod_config():
    """tries to find the MacLeod configuration file."""
    filemgt.config_file = find_config(filemgt.config_file)

def find_log_config():
    """tries to find the MacLeod logging configuration file."""
    filemgt.log_config_file = find_config(filemgt.log_config_file)

def read_config(section, key):
    """read a value from the MacLeod configuration file."""     
    # load 
    if not filemgt.CONFIG_PARSER:
        filemgt.CONFIG_PARSER = SafeConfigParser()
        filemgt.find_macleod_config()
        if len(filemgt.config_file)==0:
            filemgt.LOGGER.error("Problem reading config file from " + filemgt.config_file)
        else:
            #print("Read config file from " + filemgt.config_file)
            filemgt.conf = filemgt.CONFIG_PARSER.read(filemgt.config_file)
            filemgt.LOGGER.info('Macleod configuration read from ' + filemgt.config_file)
        
    # read from config
    return filemgt.CONFIG_PARSER.get(section,key)

        # test config parser
        #print(CONFIG_PARSER.get('converters', 'clif-to-prover9'))
     

def start_logging():
    """create a MacLeod logger and start logging."""
    if not filemgt.LOGGER:         
        find_log_config()   
        if len(filemgt.log_config_file)==0:
            print("Problem reading logging config file from " + filemgt.log_config_file)
        else:
            #print("Read logging config file from " + filemgt.log_config_file)
            logging.config.fileConfig(filemgt.log_config_file)    
            # create logger
            filemgt.LOGGER = logging.getLogger(__name__)
            filemgt.LOGGER.debug('Logging started')
            filemgt.LOGGER.debug('Logging configuration read from ' + filemgt.log_config_file)


  
def get_full_path (module_name, folder=None, ending=''):
    """determines the suitable subfolder for a given file_name."""
    if os.path.isabs(module_name):
        path = module_name
    else:
        path = filemgt.read_config('system','path') + os.sep + module_name
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
    
        
