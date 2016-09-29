'''
@author Robert Powell
@brief  Playing around with extracting useful data from the clifModuleSet setup
'''

import sys

sys.path.append('.')
sys.path.append('../')

import clif
import ClifModule

if __name__ == '__main__':

    #test_file = remove_all_comments('../qs/multidim_space_ped/ped.clif', '../qs/multidim_space_ped/ped.clif_backup')
    sentences = clif.get_sentences_from_file('qs/multidim_space_ped/ped.clif_backup')

    print len(sentences)

    nonlogical_symbols = []
    variables = []

    for sentence in sentences:
        (nonlogical_symbols, variables) = clif.get_nonlogical_symbols_and_variables (sentence)
        print sentence
        print '++', nonlogical_symbols, '++', variables
