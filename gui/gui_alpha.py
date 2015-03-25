"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

import sys
import tkFileDialog
sys.path.append("../tasks")

from Arborist import *
from summary import *
from check_consistency import *
from src.ClifModuleSet import ClifModuleSet
from Tkinter import *
import ttk
import tkMessageBox

class IORedirector(object):
    """ Some python magic """

    def __init__(self, console_text):
        """ Make the magic """

        self.console_text = console_text

class StdoutRedirector(IORedirector):
    """ Stub class to catch stdout """

    def write(self, str):
        """ Write the contents of stdout to text widget """

        self.console_text.insert(END, str, 'justified')
        # Keep the window scrolled to bottomw
        self.console_text.see(END)
        self.flush()

    def flush(self):
        """ Clear stdout? """
        #sys.stdout.flush()
        pass


class GUI(Frame):
    """ The object representing our GUI """

    def __init__(self, parent):
        """ Derp derp """

        Frame.__init__(self, parent)
        self.parent = parent

        self.arborist = False

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

    def consistency(self, canvas):
        """ Run a hardcoded consistent() """
        #change this later to catch a folder and file, not just file

        # TODO Code for actually running the consistent stuff
        module = ClifModuleSet(self.selected_file)
        visualizer = Visualizer(canvas, self.notebook)
        self.arborist = VisualArborist(visualizer)
        self.arborist.gather_nodes(module)
        self.arborist.grow_tree()
        self.arborist.prune_tree(self.arborist.tree, None, 0)
        self.arborist.weight_tree()
        self.arborist.layout_tree()
        self.arborist.draw_tree()

    def zoom(self, io):
        """ Zoom into and out of the tree """
        if io:
            self.canvas.scale("all", 0, 0, 1.1, 1.1)
        else:
            self.canvas.scale("all", 0, 0, 0.9, 0.9)

    def load_window(self):
        """ Setup the with placeholders for stuff """
        style = ttk.Style()
        style.theme_use('default')
        
        # All encompassing main frame """
        main_frame = Frame(self, borderwidth=1, relief=SUNKEN).pack(fill=BOTH, expand=1)
        
        # Top pane for choosing file and displaying path - gridded to (0,0) """
        choose_file_pane = Frame(main_frame, borderwidth=1, relief=SUNKEN)
        choose_file_pane.grid(row=0, column=0, columnspan=2, stick=E+W+S+N)
        
        # Create the dropdown option menu - pack to choose_file_pane """
        self.default_dropdown_text = StringVar()
        self.default_dropdown_text.set("Choose File(s)...")
        openFiles = OptionMenu(choose_file_pane, self.default_dropdown_text, "File...", \
                "Folder...",command=self.getOption).pack(side=LEFT) 
                
        # Buttons for clearing tree and checking consistency, for now """
        button_consist = Button(choose_file_pane, text="Check Consistency", \
                command=lambda: self.consistency(self.canvas)).pack(side=LEFT)
        button_other = Button(choose_file_pane, text="Axe the Tree", \
                command=lambda: self.deforestation()).pack(side=LEFT)
        
        # Create label that will hold the path string """
        self.selected_path = StringVar()
        self.selected_path.set("")
        self.selected_label = Label(choose_file_pane, textvariable=self.selected_path).pack(side=LEFT)
        
        # Button + Button Button - Button = Pants """
        bPlus = Button(choose_file_pane, text=" + ", \
                command=lambda: self.zoom(True)).pack(side=RIGHT)
        bMinus = Button(choose_file_pane, text=" - ", \
                command=lambda: self.zoom(False)).pack(side=RIGHT)
        
        # Now set up the two resizable paned window frames """
        paned_windows_frame = Frame(main_frame, borderwidth=1, relief=SUNKEN)
        paned_windows_frame.grid(row=1, column=0, stick=E+W+S+N)      

        # paned window will allow resizing each half of the screen """
        paned_window = PanedWindow(paned_windows_frame, orient=VERTICAL, sashrelief=SUNKEN, sashwidth=6)
        
        # Created canvas and notebook (tab stuff) inside of paned_window  """
        self.canvas = Canvas(paned_window, width=950, height=275)
        paned_window.add(self.canvas)
        self.notebook = ttk.Notebook(paned_window, name='tabs!', width=950, height=275)
        
        # Setup the tabs for the bottom pane
        self.console_tab = Frame(self.notebook)
        self.console_scrollbar = Scrollbar(self.console_tab)
        self.console_scrollbar.pack(side=RIGHT, fill=Y)
        self.console_text = Text(self.console_tab, wrap=WORD, yscrollcommand=self.console_scrollbar.set)
        #self.console_text.tag_add("justified", "%s.first" % "justified", "%s.last" % "justified")
        self.console_text.tag_add("justified", "1.0", "end")    
        self.console_text.tag_config("justified",justify=LEFT)    
        self.console_text.insert(END,"",'justified')
        self.console_text.pack(fill=BOTH, expand=1)
        self.console_scrollbar.config(command=self.console_text.yview)

#         self.raw_log = StringVar()
#         self.console_canvas = Canvas(self.console_tab, width=950,
#         self.console_scroll = Scrollbar(self.console_canvas, command=self.console_canvas.yview)
#         self.console_canvas.config(yscrollcommand=self.console_scroll.set, scrollregion=(0,0,100,1000))
#         self.console_label = Label(self.console_tab, width=940, wraplength=850, anchor=W, text="STDOUT OUTPUT HERE", \
#                 borderwidth=1, textvariable=self.raw_log, justify=LEFT, relief=SUNKEN).pack()
        self.notebook.add(self.console_tab, text="Console") 
 
        self.report_tab = Frame(self.notebook)
        self.notebook.add(self.report_tab, text="Report")    

        # Add tabs to paned window frame and pack the result 
        paned_window.add(self.notebook)
        paned_window.pack(fill=BOTH, expand=1)
        #sys.stdout = StdoutRedirector(self.console_text)

        # Proto some mouse pan support on the canvas
        self.canvas.bind("<ButtonPress-1>", self.scrollStart)
        self.canvas.bind("<B1-Motion>", self.scrollMove)


    def scrollStart(self, event):
        """ Launch internal TKinter mouse track """

        self.canvas.scan_mark(event.x, event.y)

    def scrollMove(self, event):
        """ Adjust the canvas by the amount of mouse pan """

        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def getOption(self,event):
        """ Determine what to do with the selected option """
        if (self.default_dropdown_text.get() == "File..."):
            self.askopenfilename()
        elif (self.default_dropdown_text.get() == "Folder..."):
            self.askdirectory()

    def drawTree(self, filename):
        """ Create an arborist object with selected file """

        module = ClifModuleSet(filename)
        visualizer = Visualizer(self.canvas, self.notebook)
        self.arborist = VisualArborist(visualizer)
        self.arborist.gather_nodes(module)
        self.arborist.grow_tree()
        self.arborist.prune_tree(self.arborist.tree, None, 0)
        self.arborist.weight_tree()
        self.arborist.layout_tree()
        self.arborist.draw_tree()

    def askopenfilename(self):
        """ Returns a selected directory name """
        self.selected_file = tkFileDialog.askopenfilename()
        self.selected_path.set("  Path:\t"+self.selected_file)
        self.default_dropdown_text.set("Choose File(s)...")
        self.deforestation()
        self.drawTree(self.selected_file)

    def askdirectory(self):
        """ Returns a selected directory name """
        self.selected_folder = tkFileDialog.askdirectory()
        self.selected_path.set("  Path:\t"+self.selected_folder)
        self.default_dropdown_text.set("Choose File(s)...")
        self.deforestation()

    def deforestation(self):
        """ Remove the drawn tree after selecting another file/folder to run"""
#         self.arborist.remove_tree()
        self.canvas.delete(ALL)
        
    def set_scroll(self):
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.console_text.config(scrollregion=self.console_text.bbox(ALL))
 
#     def grab(self,event):
#         self._y = event.y
#         self._x = event.x
# 
#     def drag(self,event):
#         if (self._y-event.y < 0): self.canvas.yview("scroll",-1,"units")
#         elif (self._y-event.y > 0): self.canvas.yview("scroll",1,"units")
#         if (self._x-event.x < 0): self.canvas.xview("scroll",-1,"units")
#         elif (self._x-event.x > 0): self.canvas.xview("scroll",1,"units")
#         self._x = event.x
#         self._y = event.y

def main():
    """ Create a new GUI object """
    root = Tk()
    root.geometry()
    
    #this window will NOT be resizable
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
