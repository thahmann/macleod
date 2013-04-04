'''
Created on 2011-04-29
Major revision (restructed as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os, filemgt, logging, logging.config
from ConfigParser import SafeConfigParser
import datetime

LOGGER = None
CONFIG_PARSER = None
log_config_file = 'logging.conf'
config_file = 'macleod.conf'
config_dir = 'conf'

subprocess_log_file = None

FORMATTER = None

def find_config (filename):
    """tries to find some configuration file."""
    for loc in os.path.curdir, os.path.join(os.path.curdir,filemgt.config_dir), os.path.expanduser("~"), os.environ.get("MACLEOD_CONF"):
        try:
            if not loc:
                loc = ""
            loc = os.path.join(loc,filename)
            if filemgt.LOGGER: 
                filemgt.LOGGER.debug("Looking for " + filename + " at: " + loc)
            #else:
            #    print("Looking for configuration file at: " + loc)
            if os.path.isfile(loc):
                filename = loc
                if filemgt.LOGGER: 
                    filemgt.LOGGER.debug(filename + " FOUND")
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


def find_subprocess_log_file():
    if not filemgt.subprocess_log_file:
        find_log_config()
        parser = SafeConfigParser()
        log = parser.read(filemgt.log_config_file)    
        filemgt.subprocess_log_file = filemgt.read_config("system","subprocess_log")

    
def add_to_subprocess_log(entries):
    filemgt.find_subprocess_log_file()   
    filemgt.LOGGER.debug("Writing " + str(len(entries)) + " lines to subprocess log file " + filemgt.subprocess_log_file)
    if os.path.exists(filemgt.subprocess_log_file):
        file = open(filemgt.subprocess_log_file, 'a')
    else:
        file = open(filemgt.subprocess_log_file, 'w')
    #for e in entries:
    #    filemgt.LOGGER.info("____WRITING " + e)
    file.writelines([e + "\n" for e in entries])
    file.close()
    return True    
    

def construct_log_formatter():
    """Constructs the default formatter from the logging configuration.
    Assumes we already started logging and the log file has been found."""
    filemgt.find_log_config()
    parser = SafeConfigParser()
    log = parser.read(filemgt.log_config_file)    
    # read from config
    first_handler = parser.get("handlers","keys").split(",")[0].strip()
    filemgt.FORMATTER = first_formatter = parser.get("handler_"+first_handler,"formatter")
    
def format(record):
    formatter = logging.Formatter("%(asctime)s %(name)-30s %(levelname)-8s %(message)s")
    return formatter.format(record)
#    if not filemgt.FORMATTER:
#        filemgt.construct_log_formatter()
#    parser = SafeConfigParser()
#    log = parser.read(filemgt.log_config_file)    
#    return parser.get("formatter_"+filemgt.FORMATTER,"format" % (datetime.datetime, name, level, msg))

  
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
    
        
