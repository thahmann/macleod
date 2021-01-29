#!/usr/bin/python
"""
@Author Nathaniel Swan

Anything relating to how the table is drawn for the 'report' tab, should
be controlled/implemented here
"""
import sys
sys.path.append("../")

from tkinter import *
from tkinter.ttk import *
import texttable as tt

class Report(object):
    """ class to hold all things necessary for reporting information through tables """

    def __init__(self, m, notebook):
        self.value = 1
        self.table_list = []
        self.cms = m
        self.notebook = notebook
        self.tables_drawn = []

        # for the top table
        self.defined_symbols = []
        self.undefined_symbols = []
        self.tptp_conversions = []
        self.ladr_conversions = []
        self.global_width = False
        self.root = False

    def draw_report(self):
        """ Create array of strings that will build the table """

        for table in self.table_list:
            self.tables_drawn.append(table.draw())

    def create_report_tab(self):
        """ Create the report tab in the gui """

        report_tab = Frame(self.notebook)
        report_scrollbar = Scrollbar(report_tab)
        report_scrollbar.pack(side=RIGHT, fill=Y)
        report_text = Text(report_tab, wrap=WORD, yscrollcommand=report_scrollbar.set)
        report_text.tag_add("justified", "1.0", "end")
        report_text.tag_config("justified", justify=LEFT)
        report_text.insert(END, "", 'justified') 
        for table in self.tables_drawn:
            report_text.insert(INSERT, table)

        report_text.pack(fill=BOTH, expand=1)
        report_scrollbar.config(command=report_text.yview)
        self.notebook.add(report_tab, text="Report")

    def add_table(self, table):
        """ add a table to the table_list array """
        self.table_list.append(table)

    def build_top(self):
        """ Populate the top of the table with info """
        top_table = tt.Texttable()
        self.set_root_of_cms()
        str1 = str(self.root)

        self.set_undefined_symbols()
        str2 = list(self.undefined_symbols)
        str2 = ', '.join(str(e) for e in str2)

        self.set_defined_symbols()
        str3 = list(self.defined_symbols)
        str3 = ', '.join(str(e) for e in str3)

        row = ['Ontology Information:', 'Root => '+str1+'\n\n']
        top_table.add_row(row)

        row = ['Defined Symbols: ', str3.expandtabs(4)+'\n\n\n']
        top_table.add_row(row)

        row = ['Undefined Symbols:', str2.expandtabs(4)+'\n\n']
        top_table.add_row(row)

        row = ['Conversions for Provers: ', '\n']
        top_table.add_row(row)

        top_table.set_cols_width([25, 125])
        #top_table.set_deco(top_table.BORDER | top_table.HLINES)
        self.add_table(top_table)

    def set_root_of_cms(self):
        """ return the root node (the one user has selected in gui) """
        self.root = self.cms.get_module_name()

    def set_undefined_symbols(self):
        """ set the undefined symbols from the cms """
        temp = self.cms.get_undefined_nonlogical_symbols()
        if temp != False:
            self.undefined_symbols = temp

    def set_defined_symbols(self):
        """ set the undefined symbols from the cms """
        temp = self.cms.get_defined_nonlogical_symbols()
        if temp != False:
            self.defined_symbols = temp
        #self.undefined_symbols.append(self.cms.get_undefined_nonlogical_symbols())
   # def get_tptp_conversions(self):
   # def get_ladr_conversions(self):
   # def empty_array(self, array):
   # def calculate_width(self, contents):

#test = Report()
#test.drawClifTable()

