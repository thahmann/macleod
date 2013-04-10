
if __name__ == '__main__':
    import shutil, os, sys
    from tasks import prove_lemma

    #ignores = ["theorems", "generated", "output", "consistency"]
    ignores = ["generated", "output", "consistency"]
    necessary = "_theorems"
    #necessary = false
    
    good = 0
    bad = 0
    neutral = 0
    for dir, subdirs, files in os.walk(sys.argv[1]):
        if any(ignore in dir for ignore in ignores):
            pass
        else:
            for file in files:
                #print file
                if file.endswith('.clif'):
                    if necessary and necessary not in file:
			#print "IGNORING " + file
                        continue
                    filename = os.path.normpath(os.path.join(dir.replace('qs'+os.sep,''), file))
                    #print filename
                    
                    result = prove_lemma.prove(filename, axioms_filename=None, options=['-simple'])
                    if result is True:
                        good += 1
                    elif result is False:
                        bad += 1
                    else:
                        neutral += 1

                    print "---------------------"
                    print str(good+bad+neutral) + " files in total"
                    print str(good) + " consistent"
                    print str(neutral) + " unknown"
                    print str(bad) + " inconsistent"
                    print "---------------------"

