from src import filemgt
from bin import *
import os, sys
from src.ClifModuleSet import ClifModuleSet
from bin import clif_to_ladr


#global variables
filemgt.start_logging()
tempfolder = filemgt.read_config('converters', 'tempfolder')
ignores = [tempfolder]
ending = filemgt.read_config('cl','ending')
licence.print_terms()

if __name__ == '__main__':
    options = sys.argv
    options.reverse()
    options.pop()
    folder = options.pop()
    ladr_all(folder, options)


#    for directory, subdirs, files in os.walk(folder):
#        if any(ignore in directory for ignore in ignores):
#            pass
#        else:
#            for single_file in files:
#                if single_file.endswith(ending):
#                    filename = os.path.join(directory.replace('qs\\',''), single_file)
#                    print filename
#                    m = ClifModuleSet(filename)
#                    clif_to_ladr.ladr(filename, m, options)


def ladr_all(folder, options=[]):
    for directory, subdirs, files in os.walk(folder):
        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                if single_file.endswith(ending):
                    filename = os.path.join(directory, single_file)
                    print(filename)
                    m = ClifModuleSet(filename)
                    clif_to_ladr.ladr(filename, m, options)
