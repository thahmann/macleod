"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

import sys
import tkFileDialog
sys.path.append("../tasks")

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
        self.selected_file = False
        self.selected_folder = False
        self.dir_opt = self.options = {}
        self.options['initialdir'] = '.'
        self.options['mustexist'] = False
        self.options['parent'] = self.parent
        self.options['title'] = 'This is a title'
        self.load_window()
        self.parent.title("Macleod!")
        self.scale = 1
        
        
        # define some state variables

    def consistency(self, canvas):
        """ Run a hardcoded consistent() """


		#change this later to catch a folder and file, not just file
		
        derp, clif = consistent(self.selected_file)
        self.arborist = VisualArborist(canvas)
        self.arborist.gather_nodes(clif)
        self.arborist.grow_tree()
        self.arborist.prune_tree(self.arborist.tree, None, 0)
        self.arborist.weight_tree()
        self.arborist.layout_tree()
        self.arborist.draw_tree()

    
    def zoom(self, io):
        """ Zoom into and out of the tree """
        self.scale+=io
        self.canvas.scale("all",0,0,self.scale,self.scale)
		
		    
    def load_window(self):
        """ Setup the with placeholders for stuff """

        style = ttk.Style()
        style.theme_use('default')

        right_pane = Frame(self, relief=RAISED, borderwidth=1, width=400, height=500)
        
        label_1 = Label(right_pane, text="Details").pack(fill=BOTH)     

        """ Create a notebook. This holds the tabs """
        tabs = ttk.Notebook(self, name='the cooliest stuff')
        tabs.grid(row=1, column=1, rowspan=2, stick=E+W+S+N)

        """ First tab creation """
        first_tab = Frame(tabs)
        first_tab.pack(fill=BOTH)
        tabs.add(first_tab, text="Visual")


        top_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        
        self.canvas = Canvas(top_pane, width=950, height=550, scrollregion=(0,0,700,700))
        self.canvas.pack(fill=BOTH)
        top_pane.pack(fill=BOTH, expand=1)
        
        
        """ Add vertical and horizontal scroll bars """
        hbar=Scrollbar(top_pane,orient=HORIZONTAL)
        hbar.pack(side=BOTTOM,fill=X)
        hbar.config(command=self.canvas.xview)
        
        vbar=Scrollbar(top_pane,orient=VERTICAL)
        vbar.pack(side=RIGHT,fill=Y)
        vbar.config(command=self.canvas.yview)
        
        #ccatch folder again stuff ya
        """ Footer pane for top level frame """
        path_pane = Frame(self, borderwidth=1, relief=RAISED)
        self.selected_path = StringVar()
        self.selected_label = Label(path_pane, textvariable=self.selected_path)
        self.selected_path.set("")
        path_pane.grid(row=3, column=1, columnspan=2, sticky=E+W+S+N)
        
        """ Bottom pane for the first tab """
        bottom_pane = Frame(first_tab, borderwidth=1, relief=SUNKEN)
        


        """ Button + Button Button - Button = Pants """
        bPlus = Button(bottom_pane, text=" + ", \
                command=lambda: self.zoom(0.1)).pack(side=RIGHT)
        bMinus = Button(bottom_pane, text=" - ", \
                command=lambda: self.zoom(-0.1)).pack(side=RIGHT)
        
        
        """ Creating the buttons for the first tab """
        button_consist = Button(bottom_pane, text="Check Consistency", \
                command=lambda: self.consistency(self.canvas))
        button_other = Button(bottom_pane, text="Other Thing")
        

        
        self.default_dropdown_text = StringVar()
        self.default_dropdown_text.set("Choose File(s)...")
        
        
        openFiles = OptionMenu(bottom_pane, self.default_dropdown_text, "File...", "Folder...",command=self.getOption)
        
        right_pane.grid(row=1, column=2, rowspan=2, sticky=E+W+S+N)
        
        """ Pack the buttons in the bottom pane """
        openFiles.pack(side=LEFT)
        button_consist.pack(side=LEFT)
        button_other.pack(side=LEFT)
        self.selected_label.pack(side=LEFT)
        bottom_pane.pack(fill=BOTH, expand=1)
        

        """ Add a second tab in the tabs frame """
        second_tab = Frame(tabs)
        second_tab.pack(fill=BOTH)
        tabs.add(second_tab, text="Summary")
        self.pack(fill=BOTH)
        
      

    def getOption(self,event):
        """ Determine what to do with the selected option """
        if (self.default_dropdown_text.get() == "File..."):
            self.askopenfilename()
        elif (self.default_dropdown_text.get() == "Folder..."):
            self.askdirectory()
    
    def askopenfilename(self):
        """ Returns a selected directory name """
    
        self.selected_file = tkFileDialog.askopenfilename()
        self.selected_path.set("  Path:\t"+self.selected_file)
        self.default_dropdown_text.set("Choose File(s)...")
        
    def askdirectory(self):
        """ Returns a selected directory name """
    
        self.selected_folder = tkFileDialog.askdirectory()





def main():
    """ Create a new GUI object """
    root = Tk()
    
    w = 1040
    h = 675
    # get screen width and height
    ws = root.winfo_screenwidth()#This value is the width of the screen
    hs = root.winfo_screenheight()#This is the height of the screen
    
    # calculate position x, y
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    #This is responsible for setting the dimensions of the screen and where it is
    #placed
    
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    
    #root.geometry()
    root.resizable(0,0)
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
