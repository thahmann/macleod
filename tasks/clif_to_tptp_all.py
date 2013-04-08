
if __name__ == '__main__':
    import shutil, os, sys
    from tasks import clif_to_tptp

    ignores = ["theorems", "generated", "output","consistency"]
    
    for dir, subdirs, files in os.walk(sys.argv[1]):
        if any(ignore in dir for ignore in ignores):
            pass
        else:
            for file in files:
                if file.endswith('.clif'):
                    filename = os.path.join(dir.replace('qs\\',''), file)
                    print filename
                    clif_to_tptp.tptp(filename, options=['-simple'])
