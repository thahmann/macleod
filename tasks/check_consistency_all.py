
if __name__ == '__main__':
    import shutil, os, sys
    from tasks import check_consistency

    #ignores = ["theorems", "generated", "output","consistency"]
    ignores = ["theorems", "generated", "output"]
    #necessary = "_nontrivial"
    necessary = false
    
    good = 0
    bad = 0
    neutral = 0
    for dir, subdirs, files in os.walk(sys.argv[1]):

        subdirs.sort()
        files.sort()
        
        if any(ignore in dir for ignore in ignores):
            pass
        else:
            for file in files:
                print file
                if file.endswith('.clif'):
                    if necessary and necessary not in file:
                        pass
                    filename = os.path.join(dir.replace('qs\\',''), file)
#                    print filename
                    result = check_consistency.consistent(filename, options=['-simple'])
                    if result is True:
                        good += 1
                    elif result is False:
                        bad += 1
                    else:
                        neutral += 1
    print str(good+bad+neutral) + " files in total"
    print str(good) + " consistent"
    print str(neutral) + " unknown"
    print str(bad) + " inconsistent"
