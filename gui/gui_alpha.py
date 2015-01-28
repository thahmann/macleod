"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

import sys
import tkFileDialog
sys.path.append("../tasks")

from visualizer import *
from Arborist import *
from check_consistency import *
from Tkinter import *
import ttk




class GUI(Frame):
    """ The object representing our GUI """

    def __init__(self, parent):
        """ Derp derp """
        
        Frame.__init__(self, parent)
        self.parent = parent
        
        # defining options for opening a directory
        self.dir_opt = self.options = {}
        self.options['initialdir'] = '.'
        self.options['mustexist'] = False
        self.options['parent'] = self.parent
        self.options['title'] = 'This is a title'
        self.load_window()
        self.parent.title("Macleod!")
        
        # define some state variables

    def consistency(self, canvas):
        """ Run a hardcoded consistent() """

        derp, clif = consistent("codi/codi_down")
        self.arborist = VisualArborist(canvas)
        self.arborist.gather_nodes(clif)
        self.arborist.grow_tree()
        self.arborist.prune_tree(self.arborist.tree, None, 0)
        self.arborist.weight_tree()
        self.arborist.layout_tree()
        self.arborist.draw_tree()
        self.merp.set(self.arborist.selected_node.name)

    def load_window(self):
        """ Setup the with placeholders for stuff """

        style = ttk.Style()
        style.theme_use('default')

        right_pane = Frame(self, relief=RAISED, borderwidth=1, width=400, height=500)
        
        label_1 = Label(right_pane, text="Details").pack(fill=BOTH)

        #TODO remove this later
        self.merp = StringVar()
        self.label_2 = Label(right_pane, text=self.merp).pack(fill=BOTH)
                
        self.openmenu = StringVar(right_pane)
        self.openmenu.set("Open...")
        
        openFiles = OptionMenu(right_pane, self.openmenu, "File...", "Folder...",command=self.getOption).pack(side=TOP)
        
        right_pane.grid(row=1, column=2, rowspan=2, sticky=E+W+S+N)
        
        """ Create a notebook. This holds the tabs """
        tabs = ttk.Notebook(self, name='the cooliest stuff')
        tabs.grid(row=1, column=1, rowspan=2, stick=E+W+S+N)

        """ First tab creation """
        first_tab = Frame(tabs)
        first_tab.pack(fill=BOTH)
        tabs.add(first_tab, text="Visual")


        top_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        
        canvas = Canvas(top_pane, width=700, height=500)
        canvas.pack(fill=BOTH)
        top_pane.pack(fill=BOTH, expand=1)
        
        """ Bottom pane for the first tab """
        bottom_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        
        """ Creating the buttons for the first tab """
        button_consist = Button(bottom_pane, text="Check Consistency", \
                command=lambda: self.consistency(canvas))
        button_other = Button(bottom_pane, text="Other Thing")
        
        """ Pack the buttons in the bottom pane """
        button_consist.pack(side=LEFT)
        button_other.pack(side=LEFT)
        bottom_pane.pack(fill=BOTH, expand=1)

        """ Add a second tab in the tabs frame """
        second_tab = Frame(tabs)
        second_tab.pack(fill=BOTH)
        tabs.add(second_tab, text="Summary")

        self.pack(fill=BOTH)

    def getOption(self,event):
        """ Determine what to do with the selected option """
        
        if (self.openmenu.get() == "File..."):
            self.askopenfilename()
        elif (self.openmenu.get() == "Folder..."):
            self.askdirectory()
    
    def askopenfilename(self):
        """ Returns a selected directory name """
    
        print tkFileDialog.askopenfilename()
        
    def askdirectory(self):
        """ Returns a selected directory name """
    
        print tkFileDialog.askdirectory()





def main():
    """ Create a new GUI object """

    root = Tk()
    root.geometry("1080x600")
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
