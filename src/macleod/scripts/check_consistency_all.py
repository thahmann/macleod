import os
import sys
import macleod.scripts.licence 
import macleod.scripts.check_consistency

def main():
    """Entrypoint for check consistency all"""

    licence.print_terms()

    #print(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")

    #ignores = ["theorems", "generated", "output","consistency"]
    ignores = ["theorems", "generated", "output"]
    #necessary = "_nontrivial"
    necessary = False

    good = 0
    bad = 0
    neutral = 0
    for directory, subdirs, files in os.walk(sys.argv[1]):

        subdirs.sort()
        files.sort()

        if any(ignore in directory for ignore in ignores):
            pass
        else:
            for single_file in files:
                print(single_file)
                if single_file.endswith('.clif'):
                    if necessary and necessary not in single_file:
                        pass
                    filename = os.path.join(directory.replace('qs\\',''), single_file)
#                    print filename
                    (result, _) = check_consistency.consistent(filename, options=['-simple'])
                    if result is True:
                        good += 1
                    elif result is False:
                        bad += 1
                    else:
                        neutral += 1
    print(str(good+bad+neutral) + " files in total")
    print(str(good) + " consistent")
    print(str(neutral) + " unknown")
    print(str(bad) + " inconsistent")

if __name__ == '__main__':
    sys.exit(main())
