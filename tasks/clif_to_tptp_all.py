
if __name__ == '__main__':
    import os, sys
    from tasks import clif_to_tptp

    ignores = ["theorems", "generated", "output","consistency"]
    
    for directory, subdirs, files in os.walk(sys.argv[1]):
        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                if single_file.endswith('.clif'):
                    filename = os.path.join(directory.replace('qs\\',''), single_file)
                    print filename
                    clif_to_tptp.tptp(filename, options=['-simple'])
