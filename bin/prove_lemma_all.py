
if __name__ == '__main__':
    import os, sys
    from bin import prove_lemma

    #ignores = ["theorems", "generated", "output", "consistency"]
    ignores = ["generated", "output", "consistency"]
    necessary = "_theorems"
    #necessary = false

    proofs = 0
    counterexamples = 0
    unknown = 0
    files_no = 0
    for directory, subdirs, files in os.walk(sys.argv[1]):

        subdirs.sort()
        files.sort()

        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                #print single_file
                if single_file.endswith('.clif'):
                    if necessary and necessary not in single_file:
                        #print "IGNORING " + single_file
                        continue
                    filename = os.path.normpath(os.path.join(directory.replace('qs'+os.sep,''), single_file))
                    #print filename
                    files_no += 1
                    (proofs_add, counterexamples_add, unknown_add) = prove_lemma.prove(filename, 
                                                                                       'log/lemma_summary.log',
                                                                                        axioms_filename=None,
                                                                                        options=['-simple'])
                    proofs += proofs_add
                    counterexamples += counterexamples_add
                    unknown += unknown_add

                    print("---------------------")
                    print(str(files_no) + " lemma files")
                    print(str(proofs+counterexamples+unknown) + " lemmas in total")
                    print(str(proofs) + " proofs")
                    print(str(unknown) + " unknown")
                    print(str(counterexamples) + " counterexamples")
                    print("---------------------")

