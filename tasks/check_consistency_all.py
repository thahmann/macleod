
if __name__ == '__main__':
    import shutil, os, sys
    from tasks import check_consistency

    ignores = ["theorems", "generated", "output","consistency"]
    
    good = 0
    bad = 0
    neutral = 0
    for dir, subdirs, files in os.walk(sys.argv[1]):
        if any(ignore in dir for ignore in ignores):
            pass
        else:
            for file in files:
                if file.endswith('.clif'):
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
