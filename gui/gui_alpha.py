"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

import sys
sys.path.append("../tasks")

from visualizer import *
from check_consistency import *
from Tkinter import *
import ttk

def consistency(canvas):
    """ Run a hardcoded consistent() """

    M = consistent("codi/codi")
    t = Tree(canvas, M[1])
    t.layer_tree()
    t.weight_level()
    t.draw_tree()

class GUI(Frame):
    """ The object representing our GUI """

    def __init__(self, parent):
        """ Derp derp """

        Frame.__init__(self, parent)
        self.parent = parent
        self.load_window()

        self.parent.title("Macleod!")

    def load_window(self):
        """ Setup the with placeholders for stuff """

        style = ttk.Style()
        style.theme_use('default')

        left_pane = Frame(self, relief=RAISED, borderwidth=1)
        label_1 = Label(left_pane, text="File Browser")
        label_1.pack(fill=BOTH)
        left_pane.grid(row=1, column=1, rowspan=2, sticky=E+W+S+N)

        notebook = ttk.Notebook(self, name='cool Stuff')
        notebook.grid(row=1, column=2, rowspan=2, stick=E+W+S+N)

        first_tab = Frame(notebook)
        first_tab.pack(fill=BOTH)
        notebook.add(first_tab, text="Visual")

        top_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        canvas = Canvas(top_pane, width=500, height=500)
        canvas.pack(fill=BOTH)
        top_pane.pack(fill=BOTH, expand=1)

        bottom_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        button_consist = Button(bottom_pane, text="Check Consistency", \
                command=lambda: consistency(canvas))
        button_other = Button(bottom_pane, text="Other Thing")
        button_consist.pack(side=LEFT)
        button_other.pack(side=LEFT)
        bottom_pane.pack(fill=BOTH, expand=1)

        second_tab = Frame(notebook)
        second_tab.pack(fill=BOTH)
        notebook.add(second_tab, text="Summary")

        self.pack(fill=BOTH)

def main():
    """ Create a new GUI object """

    root = Tk()
    root.geometry("800x800")
    app = GUI(root)
    root.mainloop()

#def main():
#  
#    # Toplevel GUI element
#    root = Tk()
#
#    # Use the ttk frames to hold content for compatibility
#    content = ttk.Frame(root)
#    frame = ttk.Frame(content, borderwidth=5, relief="sunken", height=500, width=500)
#
#    # Labels work like this
#    new_label = ttk.Label(content, text="A Label")
#
#    # Entry field work like this
#    new_entry = ttk.Entry(content)
#
#    # Variables used in frame work like this
#    var_one = BooleanVar() # For checkboxes
#    var_one.set(True)
#    var_two = StringVar() # For entries
#
#    # Assign those variables to elements in gui
#    checkbox_one = ttk.Checkbutton(content, text="First", variable=var_one, onvalue=True)
#    ok_button = ttk.Button(content, text="Ok")
#
#    # Grid the variables on the gui like so
#    content.grid(column=0, row=0)
#    frame.grid(column=0, row=0, columnspan=5, rowspan=5)
#
#    new_label.grid(column=1, row=1)
#    new_entry.grid(column=2, row=2)
#
#    checkbox_one.grid(column=3, row=3)
#    ok_button.grid(column=4, row=4)
#
#    root.mainloop()


if __name__ == '__main__':
    main()
