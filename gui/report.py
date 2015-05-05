#!/usr/bin/python
"""
@Author Nathaniel Swan

Anything relating to how the table is drawn for the 'report' tab, should
be controlled/implemented here
"""
import sys
sys.path.append("../src")

from Tkinter import *
from ttk import *
import texttable as tt
from ClifModuleSet import *
from ClifModule import *


class Report(object):
    """ class to hold all things necessary for reporting information through tables """
    def __init__(self, m, canvas):
        self.value = 1
        self.table_list = []
        self.cms = m
        self.canvas = canvas

        # for the top table
        self.defined_symbols = []
        self.undefined_symbols = []
        self.tptp_conversions = []
        self.ladr_conversions = []
        self.global_width = False
        self.root = False

    def draw_report(self):
        """ Pass a canvas to where the tables should be 'drawn' """
        for table in self.table_list:
            print  table.draw()

        # populate some rows
        #row = ['Ernst Happel', 'Feyenoord, Hamburg', '1970 and 1983',\
        #        'more stuff', 'more stuff']
        #table.add_row(row)
        # set column widths
        #table.set_cols_width([14, 15, 15, 20, 40])

        #set column alignments
        #table.set_cols_align(['l', 'l', 'c', 'l', 'l'])

        #finalTable = table.draw()
        #print finalTable

    def add_table(self, table):
        """ add a table to the table_list array """
        self.table_list.append(table)

    def build_top(self):
        """ Populate the top of the table with info """
        top_table = tt.Texttable()
        row = ['Ontology Information:\n\
               \tDefined Symbols: ' + self.root + '\n\
               \tUndefined Symbols: ' + self.undefined_symbols + '\n\n\
               \tConversions for Provers:']
        top_table.add_row(row)

        top_table.set_deco(top_table.BORDER)

        self.add_table(top_table)


    def set_root_of_cms(self):
        """ return the root node (the one user has selected in gui) """
        self.root = self.cms.get_module_name()

    def set_undefined_symbols(self):
        """ set the undefined symbols from the cms """
        self.undefined_symbols.append(self.cms.get_undefined_nonlogical_symbols())
   # def get_tptp_conversions(self):
   # def get_ladr_conversions(self):
   # def empty_array(self, array):
   # def calculate_width(self, contents):

#test = Report()
#test.drawClifTable()

