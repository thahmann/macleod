'''
Created on 2012-11-20

@author: Torsten Hahmann
'''

# object to keep track of the result of one theorem prover or model finder 
class ProofStatistic(object):
    filename = ''
    prover = ''
    size = ''
    success = False
    date = ''
    time = ''
    elapsed = ''

    MACE4    = 'Mace4'
    PROVER9  = 'Prover9'
    PARADOX3 = 'Paradox3' 
    VAMPIRE  = 'Vampire'

    def __init__(self, name=''):
        self.prover = name
