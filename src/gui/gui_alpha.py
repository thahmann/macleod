"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

from Tkinter import *
import ttk

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

        left_pane = Frame(self, relief=RAISED, borderwidth=1)
        label_1 = Label(left_pane, text="File Browser", height=20)
        label_1.pack(fill=BOTH)
        left_pane.grid(row=1, column=1, rowspan=2, sticky=E+W+S+N)

        right_top_pane = Frame(self, borderwidth=1, relief=SUNKEN)
        label_2 = Label(right_top_pane, text="TREE", width=20)
        label_2.pack(fill=BOTH)
        right_top_pane.grid(row=1, column=2, sticky=E+W+S+N)

        right_bottom_pane = Frame(self, borderwidth=1, relief=SUNKEN)
        button_consist = Button(right_bottom_pane, text="Check Consistency")
        button_other = Button(right_bottom_pane, text="Other Thing")
        button_consist.pack(side=LEFT)
        button_other.pack(side=LEFT)
        right_bottom_pane.grid(row=2, column=2, sticky=E+W+S+N)

        self.pack(fill=BOTH)

def main():
    """ Create a new GUI object """

    root = Tk()
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
