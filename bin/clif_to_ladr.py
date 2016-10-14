'''
Created on 2013-03-22

@author: Torsten Hahmann
'''

from bin import *
import sys
from src.ClifModuleSet import ClifModuleSet


def ladr(filename, m, options=[]):

    if '-cumulate' in options:
        # translate into a single ladr single_file
        single_file = m.get_single_ladr_file()
        print("")
        print("+++++++++++++++++++++")
        print("Files created:")
        print("")
        print(single_file)
        print("+++++++++++++++++++++")
    elif '-module' in options:
        single_file = m.get_top_module().get_p9_file_name()
        print("")
        print("+++++++++++++++++++++")
        print("Files created:")
        print("")
        print(single_file)
        print("+++++++++++++++++++++")

    else:
        files = m.get_ladr_files()
        print("")
        print("+++++++++++++++++++++")
        print("Files created:")
        print("")
        for single_file in files:
            print(single_file)
        print("+++++++++++++++++++++")    


if __name__ == '__main__':
    licence.print_terms()
    # global variables
    options = sys.argv
    options.reverse()
    options.pop()
    filename = options.pop()
    ladr(filename, options)

