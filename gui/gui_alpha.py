#! /usr/bin/env python
"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

import sys
import tkFileDialog
import time
sys.path.append("../tasks")

from Arborist import *
from summary import *
from check_consistency import *
from clif_to_ladr import *
from clif_to_tptp import *
from prove_lemma import *
from check_nontrivial_consistency import *
from src.ClifModuleSet import ClifModuleSet
from Tkinter import *
import ttk
import tkMessageBox
import logging

LOG = logging.getLogger(__name__)

imgdir = os.path.join(os.path.dirname(__file__), 'img')

def btn_press(event):
    """ Notebook tab close action """

    x, y, widget = event.x, event.y, event.widget
    elem = widget.identify(x, y)
    index = widget.index("@%d,%d" % (x, y))

    if "close" in elem:
        if index != 0 and index != 1:
            print index, elem
            widget.state(['pressed'])
            widget.pressed_index = index

def btn_release(event):
    """ Notebook tab close/release action """

    x, y, widget = event.x, event.y, event.widget

    if not widget.instate(['pressed']):
        return

    elem = widget.identify(x, y)
    index = widget.index("@%d,%d" % (x, y))

    if "close" in elem and widget.pressed_index == index:
        widget.forget(index)
        widget.event_generate("<<NotebookClosedTab>>")

    widget.state(["!pressed"])
    widget.pressed_index = None


class StdoutRedirector(object):
    """ Stub class to catch stdout """

    def __init__(self, console_text, window):
        """ Make the magic """

        self.console_text = console_text
        self.window = window

    def write(self, str):
        """ Write the contents of stdout to text widget """

        self.console_text.insert(END, str, 'justified')
        self.console_text.see(END)
        self.window.update()

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
        self.module = False

        # defining options for opening a directory
        self.selected_file = False
        self.selected_folder = False

        self.dir_opt = self.options = {}
        self.options['initialdir'] = '.'
        self.options['mustexist'] = False
        self.options['parent'] = self.parent
        self.options['title'] = 'This is a title'

        self.parent.title("Macleod!")
        self.scale = 1
        #self.load_window()

    def consistency(self, canvas):
        """ Run a hardcoded consistent() """
        #change this later to catch a folder and file, not just file

        # TODO Code for actually running the consistent stuff
        consistent(self.selected_file)

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
        style.element_create("close", "image", "img_close", \
        ("active", "pressed", "!disabled", "img_closepressed"), \
        ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("ButtonNotebook", [("ButtonNotebook.client", {"sticky": "nswe"})])
        style.layout("ButtonNotebook.Tab", [
            ("ButtonNotebook.tab", {"sticky": "nswe", "children": \
                    [("ButtonNotebook.padding", {"side": "top", "sticky": "nswe", "children": \
                    [("ButtonNotebook.focus", {"side": "top", "sticky": "nswe", "children": \
                    [("ButtonNotebook.label", {"side": "left", "sticky": ''}), \
                    ("ButtonNotebook.close", {"side": "left", "sticky": ''})]})]})]})])
        
        # All encompassing main frame """
        self.main_frame = Frame(self, borderwidth=1, relief=SUNKEN).pack(fill=BOTH, expand=1)
        
        # Top pane for choosing file and displaying path - gridded to (0,0) """
        self.choose_file_pane = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)
        self.choose_file_pane.grid(row=0, column=0, columnspan=2, stick=E+W+S+N)
        
        # Create the dropdown option menu - pack to choose_file_pane """
        self.default_dropdown_text = StringVar()
        self.default_dropdown_text.set("Choose File(s)...")
        openFiles = OptionMenu(self.choose_file_pane, self.default_dropdown_text, "File...", \
                "Folder...",command=self.getOption).pack(side=LEFT) 

        # Create label that will hold the path string """
        self.selected_path = StringVar()
        self.selected_path.set("")
        self.selected_label = Label(self.choose_file_pane, textvariable=self.selected_path).pack(side=LEFT)
        
        # Button + Button Button - Button = Pants """
        bPlus = Button(self.choose_file_pane, text=" + ", \
                command=lambda: self.zoom(True)).pack(side=RIGHT)
        bMinus = Button(self.choose_file_pane, text=" - ", \
                command=lambda: self.zoom(False)).pack(side=RIGHT)

        # Now set up the two resizable paned window frames """
        paned_windows_frame = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)
        paned_windows_frame.grid(row=1, column=0, stick=E+W+S+N)

        # paned window will allow resizing each half of the screen """
        paned_window = PanedWindow(paned_windows_frame, orient=VERTICAL, sashrelief=SUNKEN, sashwidth=6)

        # Created canvas and notebook (tab stuff) inside of paned_window  """
        self.canvas = Canvas(paned_window, width=950, height=275)
        paned_window.add(self.canvas)
        self.notebook = ttk.Notebook(paned_window, name='tabs!', width=950, height=275)
        print ttk.Style().theme_names
        print self.notebook.winfo_class()
        self.notebook.configure(style="ButtonNotebook")
        # Setup the tabs for the bottom pane
        self.console_tab = Frame(self.notebook)
        self.console_scrollbar = Scrollbar(self.console_tab)
        self.console_scrollbar.pack(side=RIGHT, fill=Y)
        self.console_text = Text(self.console_tab, wrap=WORD, yscrollcommand=self.console_scrollbar.set)
        #self.console_text.tag_add("justified", "%s.first" % "justified", "%s.last" % "justified")
        self.console_text.tag_add("justified", "1.0", "end")
        self.console_text.tag_config("justified", justify=LEFT)
        self.console_text.insert(END,"",'justified')
        self.console_text.pack(fill=BOTH, expand=1)
        self.console_scrollbar.config(command=self.console_text.yview)

        self.notebook.add(self.console_tab, text="Console")

        self.report_tab = Frame(self.notebook)
        self.notebook.add(self.report_tab, text="Report")

        # Add tabs to paned window frame and pack the result
        paned_window.add(self.notebook)
        paned_window.pack(fill=BOTH, expand=1)

        sys.stdout = StdoutRedirector(self.console_text, self.parent)

        # Proto some mouse pan support on the canvas
        self.canvas.bind("<ButtonPress-1>", self.scrollStart)
        self.canvas.bind("<B1-Motion>", self.scrollMove)
        
    def create_task_pane(self, identifier):
        # Now set up the two resizable paned window frames """
        self.task_pane = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)

        if(identifier == "file"):
            consist = Button(self.task_pane, text="Check Consistency", \
                command=lambda: consistent(self.selected_file,self.module)).pack(side=TOP) 
            non_trivial_consist = Button(self.task_pane, text="Check Non-Trivial Consistency", \
                command=lambda: nontrivially_consistent(self.selected_file, self.module)).pack(side=TOP)
            clif_to_ladr = Button(self.task_pane, text="Clif to LADR", \
                command=lambda: ladr(self.selected_file, self.module)).pack(side=TOP)
            clif_to_tptp = Button(self.task_pane, text="Clif to TPTP", \
                command=lambda: tptp(self.selected_file, self.module)).pack(side=TOP)
            prove_lemma = Button(self.task_pane, text="Prove Lemma", \
                command=lambda: self.consistency(self.canvas)).pack(side=TOP)           
        else:
            button_other = Button(self.task_pane, text="Axe the Tree", \
                    command=lambda: self.deforestation()).pack(side=TOP)
#         button_consist = Button(choose_file_pane, text="Check Consistency", \
#                 command=lambda: self.consistency(self.canvas)).pack(side=LEFT)
#         button_consist = Button(choose_file_pane, text="Check Consistency", \
#                 command=lambda: self.consistency(self.canvas)).pack(side=LEFT)
#         button_consist = Button(choose_file_pane, text="Check Consistency", \
#                 command=lambda: self.consistency(self.canvas)).pack(side=LEFT)
#         button_consist = Button(choose_file_pane, text="Check Consistency", \
#                 command=lambda: self.consistency(self.canvas)).pack(side=LEFT)  
        
        self.task_pane.grid(row=0, column=1, stick=E+W+S+N, rowspan=2)
        # going to need to reset this pane, or remove it, then redraw, lets say if user picks a folder,
        # and then decides to choose a file
        
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

        self.module = ClifModuleSet(filename)
        visualizer = Visualizer(self.canvas, self.notebook)
        self.arborist = VisualArborist(visualizer)
        self.arborist.gather_nodes(self.module)
        self.arborist.grow_tree()
        self.arborist.deep_clean()
        self.arborist.prune_tree_bfs(self.arborist.tree, 0)
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
        self.create_task_pane("file")

    def askdirectory(self):
        """ Returns a selected directory name """

        self.selected_folder = tkFileDialog.askdirectory()
        self.selected_path.set("  Path:\t"+self.selected_folder)
        self.default_dropdown_text.set("Choose File(s)...")
        self.deforestation()
        self.create_task_pane("folder")

    def deforestation(self):
        """ Remove the drawn tree after selecting another file/folder to run"""
#         self.arborist.remove_tree()
        self.canvas.delete(ALL)
        for i in range(len(self.notebook.tabs())):
            if i > 1:
                self.notebook.forget(i)

    def set_scroll(self):
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.console_text.config(scrollregion=self.console_text.bbox(ALL))

def main():
    """ Create a new GUI object """

    root = Tk()

    i1 = PhotoImage("img_close", file=os.path.join(imgdir, 'close.gif'))
    i2 = PhotoImage("img_closeactive", file=os.path.join(imgdir, 'close_active.gif'))
    i3 = PhotoImage("img_closepressed", file=os.path.join(imgdir, 'close_pressed.gif'))

    root.bind_class("TNotebook", "<ButtonPress-1>", btn_press, True)
    root.bind_class("TNotebook", "<ButtonRelease-1>", btn_release)

    root.geometry()
    root.resizable(0,0)
    app = GUI(root)
    app.load_window()
    root.mainloop()

if __name__ == '__main__':
    main()
