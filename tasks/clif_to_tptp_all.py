from src import filemgt
from tasks import *

if __name__ == '__main__':
    import os, sys
    from tasks import clif_to_tptp

    filemgt.start_logging()
    tempfolder = filemgt.read_config('converters', 'tempfolder')
    
    ignores = [tempfolder]
    
    ending = filemgt.read_config('cl','ending')

    licence.print_terms()
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    folder = options.pop()

    
    for directory, subdirs, files in os.walk(folder):
        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                if single_file.endswith(ending):
                    filename = os.path.join(directory.replace('qs\\',''), single_file)
                    print filename
                    clif_to_tptp.tptp(filename, options)
