'''
Created on 2011-04-29
Major revision (restructed as a module with new name filemgt) on 2013-03-14

@author: Torsten Hahmann
'''

import os

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
def get_name_with_subfolder (complete_path_and_name, folder, ending=''):
    
    #print complete_path_and_name
        
    SUBFOLDERS = set([read_config('ladr','folder'), 
                      read_config('tptp','folder'), 
                      read_config('output','folder'),
                      read_config('converters','tempfolder')])
        
    (dir, filename) = os.path.split(complete_path_and_name)
    if (len(dir)>0 and len(filename)>0):
        # strip other folder names:
        directory_parts = dir.rsplit(os.sep,1)
#            if len(directory_parts)==2:
#                print directory_parts[1]
        if len(directory_parts)==2:
            #directory_parts[1] = '/' + directory_parts[1]
            #print directory_parts[1]
            # remove special folder from path
            if directory_parts[1] in SUBFOLDERS:
                dir = directory_parts[0]
#                else:
#                    print 'stripped subfolder ' + directory_parts[1] 
        directory = os.path.join(dir,folder)
        out_file_name = os.path.join(directory,filename + ending)
    else:
        directory = folder
        out_file_name = os.path.join(directory, filename + ending)
    # create the directory if necessary
    if not os.path.exists(directory):
        os.makedirs(directory)
    return out_file_name
    
    
        
