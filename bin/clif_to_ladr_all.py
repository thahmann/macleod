import os, sys, datetime

#print(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")

from bin import licence, clif_to_ladr
import macleod.Filemgt as filemgt
from macleod.ClifModuleSet import ClifModuleSet


#global variables
filemgt.start_logging()
tempfolder = filemgt.read_config('converters', 'tempfolder')
ignores = [tempfolder]
ending = filemgt.read_config('cl','ending')

if __name__ == '__main__':
	licence.print_terms()
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
