#!/usr/bin/python

"""
Robert Powell
Nov 10, 2014

Functionality to generate a visual tree of a ClifModuleSet
"""

from Tkinter import *
import ttk
# Bootstrapped GUI Stuff -- Will be pushed into gui_alpha.py

class Tree(object):
    """ Drawable extension of the ClifModuleSet """

    def __init__(self, canvas, clif_set):
        """ Create a tree with a canvas to draw on and the root node """

        self.canvas = canvas
        self.max_width = canvas.winfo_width()
        self.clif_set = clif_set
        self.root = clif_set.get_top_module()
        self.levels = []

#    def generate_tree(self):
#        """ Take a ClifModuleSet and translate it to a generic tree """
#
#        self.root = Node(self.canvas, 0, [], None, \
#                self.clif_set.imports(self.clif_set.module_name))
#
#        queue = []
#        queue.append([self.clif_set.imports(self.clif_set.module_name)])
#        while queue:
#            current_level = queue.pop(0)
#            next_level = []
#            for node in current_level:
#                ### Create a new node for the tree ###
#                node_children = []
#                node_depth = node.depth
#                if node.parents: node_parent = node.parents
#                else: node_parent = None
#
#                self.nodes.append(Node(self.canvas, node_depth, node_parent, node_children))
#
#                ### End of new node creation ###
#                next_level += node.children
#            queue.append(next_level)
#
#        for node in self.clif_set.imports:
#            node_name = node.module_name
#            node_depth = node.depth
#            node_canvas = self.canvas

    def layer_tree(self):
        """ A BFS search to draw each level of tree """

        queue = []
        queue.append([self.root])
        while queue != [[]]:
            print queue
            current_level = queue.pop(0)
            self.levels.append(current_level)
            next_level = []
            for node in current_level:
                next_level += list(node.get_imports_as_modules())
            queue.append(next_level)

    def weight_level(self):
        """ Traverse through the levels and weight each node """

        #TODO: It's called recursion, I should learn to use it...
        print self.levels
        for level in reversed(self.levels):
            for node in level:
                if len(node.get_imports_as_modules()) <= 1:
                    node.width = 10
                else:
                    for child in node.get_imports_as_modules():
                        node.width += child.width

    def draw_tree(self):
        """ Draw the tree from the top down with correct spacing """

        for level in self.levels:
            sorted_level = sorted(level, key=lambda n: n.width, reverse=True)
            spacer = -sorted_level[0].width
            print spacer
            for node in sorted_level:
                node.get_coordinates(spacer)
                node.draw(self.canvas)
                spacer += node.width


class Node(object):
    """ Basic abstraction for each ClifModule """

    def __init__(self, canvas, depth, children, parent, module):
        """ Create a node """
        #TODO: Remember to translate to a ClifModule

        self.canvas = canvas
        self.depth = depth
        self.children = children
        self.parent = parent
        self.x = 0
        self.y = 0
        self.module = module

    def get_coordinates(self, offset, modifier=10):
        """ Establish a nodes correct coordinates """

        self.y = self.depth * modifier
        if self.parent:
            self.x = self.parent.x + offset

        self.draw()

    def draw(self, size=10):
        """ Call to Tkinter to draw the node on a canvas """

        print "I'm DRAWING SOMETHING!"

        self.canvas.create_rectangle(self.x - size, self.y - size, \
                self.x + size, self.y + size)


def GUI(SET):
    """ Main method to launch the app """

    root = Tk()
    frame = ttk.Frame(root)
    canvas = Canvas(frame)

    t = Tree(canvas, SET)
    t.layer_tree()
    t.weight_level()
    t.draw_tree()

    canvas.pack(fill=BOTH, expand=1)
    frame.grid(column=0, row=0)

    root.mainloop()

if __name__ == '__main__':
    main()
