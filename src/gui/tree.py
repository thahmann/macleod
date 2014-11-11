#!/usr/bin/python

"""
Robert Powell
Nov 10, 2014

Functionality to generate a visual tree of a ClifModuleSet
"""

from Tkinter import *
import ttk
# Bootstrapped GUI Stuff -- Will be pushed into gui_alpha.py

class Node(object):
    """ Basic abstraction for each ClifModule """

    def __init__(self, canvas, center_x, center_y):
        """ Create a node """
        #TODO: Do something with the ClifModule

        self.canvas = canvas
        self.x = center_x
        self.y = center_y

    def draw(self, size=50):
        """ Draw a node as a rectangle about its center """

        self.canvas.create_rectangle(self.x - size, self.y - size, \
                self.x + size, self.y + size)


def main():
    """ Main method to launch the app """

    root = Tk()
    frame = ttk.Frame(root)
    canvas = Canvas(frame)

    test_node = Node(canvas, 50, 50)
    test_node.draw(25)

    canvas.pack(fill=BOTH, expand=1)
    frame.grid(column=0, row=0)

    root.mainloop()

if __name__ == '__main__':
    main()
