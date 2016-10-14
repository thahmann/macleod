'''
Created on 2012-11-20
Refactored on 2013-03-18

@author: Torsten Hahmann
'''
from . import process, filemgt

def select_lemma (self, tptp_in_file, number, total, use_previous = False):
    """select one lemma as conjecture.
    number -- the lemma to prove (from the start of all axioms
    total -- the total number of lemmas contained in the single_file (will remove all except the one we want to prove)
    use_previous -- reuse the previous lemmas in the same single_file, i.e., do not delete earlier lemmas (assume they are provable)"""

    single_file = open(tptp_in_file, 'r')
    text = single_file.readlines()
    single_file.close()

    out_text = []
    count = 0
    for i in range(0,len(text)):
        if text[i].startswith('fof(') or text[i].startswith('cnf('):
            count += 1
            # delete all other lemmas; do not delete previous lemmas if instructed so
            if (count<number and not use_previous) or (count>number and count<=total):
                # remove line; do not copy to output
                pass
            elif count==number:
                out_text.append(line[i].replace(',axiom,', ',conjecture,'))
            else:
                out_text.append(line[i])

    single_file = open(tptp_in_file, 'w+')
    single_file.writelines(out_text)
    out_file.close()


# get the version of the currently installed vampire
def get_version(self):
    vampire = process.startInteractiveProcess(filemgt.read_config('vampire','command') + ' --version')
    # only one line as output expected
    return vampire.stdout.readline()

