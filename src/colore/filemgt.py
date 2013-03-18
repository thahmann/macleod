'''
Created on 2011-04-29
Major revision (restructed as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os, filemgt

#CONFIG_PARSER: reads
CONFIG_PARSER = None
config_file = 'macleod.conf'
config_dir = 'conf'

# tries to find and then read the MacLeod configuration file
def find_config():
    import filemgt
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
                break
        except IOError:
            pass


# read a value from the MacLeod configuration file     
def read_config(section, key):
    import filemgt
    from ConfigParser import SafeConfigParser
    # load 
    if not filemgt.CONFIG_PARSER:
        filemgt.CONFIG_PARSER = SafeConfigParser()
        find_config()
        conf = filemgt.CONFIG_PARSER.read(config_file)
        if len(conf)==0:
            print("Problem reading config file from " + os.path.abspath(os.path.curdir) + filemgt.config_file)
        
    # read from config
    return filemgt.CONFIG_PARSER.get(section,key)

        # test config parser
        #print(CONFIG_PARSER.get('converters', 'clif-to-prover9'))
     

  
# determines the suitable subfolder for a given file_name
def get_full_path (module_name, folder=None, ending=''):
    path = filemgt.read_config('cl','path') + os.sep + module_name
    if folder:
        path = os.path.dirname(path) + os.sep + folder + os.sep + os.path.basename(path)
    # create this folder if it does not exist yet
    path = os.path.normpath(path)
    if not os.path.isdir(os.path.dirname(path)):
        if os.mkdir(os.path.dirname(path)):
            print "Created folder " + path
    
    return os.path.abspath(path + ending)

    

    
        
