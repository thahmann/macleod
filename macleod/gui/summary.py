#!/usr/bin/python
"""
@Author Robert Powell

Anything that the tree needs to know about the GUI should happen here
"""

import sys
sys.path.append("../src")

from tkinter import *
from tkinter.ttk import *
import os
import platform
import src.filemgt

EDITOR = None

def find_system_editor():
    """ Configure to open system preferred editor """

    if platform.sys == 'DARWIN':
        EDITOR = os.environ['EDITOR']
    else:
        editor = 'open'

    def edit_file(path):
        """ Launch the system editor on provided file """

        full_path = src.filemgt.get_full_path(path)
        os.system(editor + ' ' + full_path)

    return edit_file

def edit_external_file(module_name):
    """ Open system editor on file """

    global EDITOR

    if not EDITOR:
        EDITOR = find_system_editor()

    EDITOR(module_name + '.clif')

class Visualizer(object):
    """ Create the link between the VisualAborist and GUI """

    def __init__(self, canvas, notebook):

        self.canvas = canvas
        self.notebook = notebook
        self.tabs = {}


    def create_tab(self, node):
        """ Create node tab in GUI notebook """

        if node.name not in self.tabs:
            node_tab = Frame(self.notebook)
            node_scrollbar = Scrollbar(node_tab)
            node_scrollbar.pack(side=RIGHT, fill=Y)

            self.notebook.add(node_tab, text=node.name)
            self.tabs[node.name] = node_tab
            self.fill_node_tab(node_tab, node)
        else:
            tab = self.tabs[node.name]
            self.notebook.add(tab, text=node.name)

    def fill_node_tab(self, node_tab, node):
        """ Extract info about a node """

        node_info = Text(node_tab, wrap=WORD)
        node_info.tag_add("justified", "1.0", "end")
        node_info.tag_config("justified", justify=LEFT)
        node_info.insert(END, "", 'justified')
        node_info.pack(fill=BOTH, expand=1)

        hyperlink = HyperLink(node_info)

        node_info.insert(INSERT, 'Name: ')
        node_info.insert(INSERT, node.name + '\n', \
                hyperlink.add(lambda: edit_external_file(node.name)))

        node_info.insert(INSERT, 'Depth: ' + str(node.depth) + '\n')
        if node.visual_parent:
            node_info.insert(INSERT, 'Parent: ' + node.visual_parent.name + '\n')

        node_info.insert(INSERT, '\n\n')

        node_info.insert(INSERT, 'All Parents:\n')
        node_info.insert(INSERT, '------------\n')
        for parent in node.parents:
            node_info.insert(INSERT, parent.name, \
                    hyperlink.add(lambda: edit_external_file(parent.name)))
            node_info.insert(INSERT, ' ')
        node_info.insert(INSERT, '\n')
        node_info.insert(INSERT, '\n')

        node_info.insert(INSERT, 'All Children:\n')
        node_info.insert(INSERT, '-------------\n')
        for child in node.children:
            node_info.insert(INSERT, child.name, \
                    hyperlink.add(lambda: edit_external_file(child.name)))
            node_info.insert(INSERT, ' ')
        node_info.insert(INSERT, '\n')
        node_info.insert(INSERT, '\n')

        node_info.insert(INSERT, 'Definitions:\n')
        node_info.insert(INSERT, '------------\n')
        for definition in node.definitions:
            node_info.insert(INSERT, definition.name, \
                    hyperlink.add(lambda: edit_external_file(node.name)))
            node_info.insert(INSERT, ' ')
        node_info.insert(INSERT, '\n')
        node_info.insert(INSERT, '\n')

        node_info.insert(INSERT, 'Defined Symbols:\n')
        node_info.insert(INSERT, '----------------\n')
        for definition in node.definitions:
            # node_info.insert(INSERT, definition.name + '\n')
            for (symbol, arity) in definition.module.get_defined_symbols():
                node_info.insert(INSERT, str(symbol))
            node_info.insert(INSERT, '\n')
        node_info.insert(INSERT, '\n')

        node_info.insert(INSERT, 'Used Symbols:\n')
        node_info.insert(INSERT, '-------------\n')
        for (symbol, arity) in node.module.get_nonlogical_symbols():
            node_info.insert(INSERT, str(symbol) + ' ')

        defs = []
        for definition in node.definitions:
            for (symbol, arity) in definition.module.get_nonlogical_symbols():
                if symbol not in defs:
                    node_info.insert(INSERT, str(symbol) + ' ')
                    defs.append(symbol)



class HyperLink(object):
    """ Hyperlinks in TKinter! """

    def __init__(self, text):
        """ Create a text widget with hyperlink functionality """

        self.text = text
        self.text.tag_config('hyper', foreground='blue', underline=1)
        self.text.tag_bind('hyper', '<Enter>', self._enter)
        self.text.tag_bind('hyper', '<Leave>', self._leave)
        self.text.tag_bind('hyper', '<Button-1>', self._click)
        self.links = {}

    def reset(self):
        """ Clear all internal links """

        self.links = {}

    def add(self, action):
        """ Add action to link text """

        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return 'hyper', tag

    def _enter(self, event):
        """ Change mouse cursor on hover """

        self.text.config(cursor='hand2')

    def _leave(self, event):
        """ Restore normal cursor on leave """

        self.text.config(cursor='')

    def _click(self, event):
        """ Execute link action if clicked """

        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == 'hyper-':
                self.links[tag]()
                return
