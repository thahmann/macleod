
if __name__ == '__main__':
    import shutil, os, sys
    from tasks import prove_lemma

    #ignores = ["theorems", "generated", "output", "consistency"]
    ignores = ["generated", "output", "consistency"]
    necessary = "_theorems"
    #necessary = false
    
    proofs = 0
    counterexamples = 0
    unknown = 0
    files_no = 0
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
                    files_no += 1
                    (proofs_add, counterexamples_add, unknown_add) = prove_lemma.prove(filename, axioms_filename=None, options=['-simple'])
                    proofs += proofs_add
                    counterexamples += counterexamples_add
                    unknown += unknown_add

                    print "---------------------"
                    print str(files_no) + " lemma files"
                    print str(proofs+counterexamples+unknown) + " lemmas in total"
                    print str(proofs) + " proofs"
                    print str(unknown) + " unknown"
                    print str(counterexamples) + " counterexamples"
                    print "---------------------"

