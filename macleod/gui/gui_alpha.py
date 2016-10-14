#! /usr/bin/env python
"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod
"""

from macleod.bin import *
from macleod import *

# source
#from src.ClifModuleSet import *
#from src.filemgt import *

# visual components
from gui.Arborist import *
from gui.summary import *
from gui.table import *

# task scripts
import logging

from tasks.check_consistency import *
from tasks.clif_to_ladr import *
from tasks.clif_to_tptp import *
from tasks.prove_lemma import *
from tasks.check_nontrivial_consistency import *
from tasks.check_consistency_all import *
from tasks.clif_to_ladr_all import *
from tasks.clif_to_tptp_all import *
from tasks.prove_lemma_all import *
from tasks.delete_output import *
from tkinter import *
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog

LOG = logging.getLogger(__name__)
img_dir = os.path.join(os.path.dirname(__file__), 'img')

def btn_press(event):
    """ Notebook tab close action """

    x_pos, y_pos, widget = event.x, event.y, event.widget
    elem = widget.identify(x_pos, y_pos)
    index = widget.index("@%d,%d" % (x_pos, y_pos))
    if "close" in elem:
        if index != 0 and index != 1:
            print(index, elem)
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


class IORedirector(object):
    """ Stub class to catch stdout """

    def __init__(self, console_text):
        """ Make the magic """

        self.console_text = console_text

class StdoutRedirector(IORedirector):
    """ Redirect Standard out to a canvas """

    def write(self, text_content):
        """ Write the contents of stdout to text widget """
        self.console_text.insert(END, text_content, 'justified')
        self.console_text.see(END)

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
        self.report = False
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

        """ Main Window things """
        self.choose_file_pane = None
        self.selected_path = StringVar()
        self.main_frame = None
        self.default_dropdown_text = StringVar()
        self.canvas = False
        self.task_pane = False
        self.selected_label = None
        self.selected_file = None
        self.selected_folder = None

        """ Notebook and PanedWindow section """
        self.notebook = None
        self.paned_window = False
        self.paned_windows_frame = False
        self.console_tab = False
        self.console_scrollbar = False
        self.console_text = False
        self.report_tab = False
        self.report_scrollbar = False
        self.report_text = False
        #self.load_window()

    def consistency(self):
        """ Run a hardcoded consistent() """
        consistent(self.selected_file)

    def zoom(self, io):
        """ Zoom into and out of the tree """
        if io:
            self.canvas.scale("all", 0, 0, 1.1, 1.1)
            self.arborist.adjust_text(io)
        else:
            self.canvas.scale("all", 0, 0, 0.9, 0.9)
            self.arborist.adjust_text(io)

    def load_window(self):
        """ Setup the with placeholders for stuff """

        style = tkinter.ttk.Style()
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

        # All encompassing main frame
        self.main_frame = Frame(self, borderwidth=1, relief=SUNKEN).pack(fill=BOTH, expand=1)

        # Top pane for choosing file and displaying path - gridded to (0,0)
        self.choose_file_pane = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)
        self.choose_file_pane.grid(row=0, column=0, columnspan=1, stick=E+W+S+N)

        # Create the dropdown option menu - pack to choose_file_pane
        #self.default_dropdown_text = StringVar()
        self.default_dropdown_text.set("Choose File(s)...")
        open_files = OptionMenu(self.choose_file_pane, self.default_dropdown_text, "File...", \
                "Folder...", command=self.getOption)
        open_files.pack(side=LEFT)

        # Create label that will hold the path string
        #self.selected_path = StringVar()
        self.selected_path.set("")
        self.selected_label = Label(self.choose_file_pane, textvariable=self.selected_path)
        self.selected_label.pack(side=LEFT)

        zoom_in = Button(self.choose_file_pane, text=" + ", command=lambda: self.zoom(True))
        zoom_in.pack(side=RIGHT)
        zoom_out = Button(self.choose_file_pane, text=" - ", command=lambda: self.zoom(False))
        zoom_out.pack(side=RIGHT)

        # Now set up the two resizable paned window frames """
        self.paned_windows_frame = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)
        self.paned_windows_frame.grid(row=1, column=0, stick=E+W+S+N)

        # paned window will allow resizing each half of the screen
        self.paned_window = PanedWindow(self.paned_windows_frame, \
                orient=VERTICAL, sashrelief=SUNKEN, sashwidth=6)

        # Created canvas and notebook (tab stuff) inside of paned_window  """
        self.canvas = Canvas(self.paned_window) #, width=900, height=275)
        self.paned_window.add(self.canvas)
        self.notebook = tkinter.ttk.Notebook(self.paned_window, name='tabs!')# width=950, height=275)
        #print ttk.Style().theme_names
        #print self.notebook.winfo_class()
        self.notebook.configure(style="ButtonNotebook")

        # Setup the tabs for the bottom pane
        self.console_tab = Frame(self.notebook)
        self.console_scrollbar = Scrollbar(self.console_tab)
        self.console_scrollbar.pack(side=RIGHT, fill=Y)
        self.console_text = Text(self.console_tab, wrap=WORD, \
                yscrollcommand=self.console_scrollbar.set)
        #self.console_text.tag_add("justified", "%s.first" % "justified", "%s.last" % "justified")
        self.console_text.tag_add("justified", "1.0", "end")
        self.console_text.tag_config("justified", justify=LEFT)
        self.console_text.insert(END, "", 'justified')
        self.console_text.pack(fill=BOTH, expand=1)
        self.console_scrollbar.config(command=self.console_text.yview)
        self.notebook.add(self.console_tab, text="Console")


        # Add tabs to paned window frame and pack the result
        self.paned_window.add(self.notebook)
        self.paned_window.pack(fill=BOTH, expand=1)

        sys.stdout = StdoutRedirector(self.console_text)

        # Proto some mouse pan support on the canvas
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)

    def create_task_pane(self, identifier):
        """  set up the two resizable paned window frames """
        self.task_pane = Frame(self.main_frame, borderwidth=1, relief=SUNKEN)
        print(self.selected_folder)
        if identifier == "file":
            consist = Button(self.task_pane, text="Check Consistency", \
                command=lambda: consistent(self.selected_file,self.module))
            consist.pack(side=TOP)
            non_trivial_consist = Button(self.task_pane, text="Check Non-Trivial Consistency", \
                command=lambda: nontrivially_consistent(self.selected_file, self.module))
            non_trivial_consist.pack(side=TOP)
            clif_to_ladr = Button(self.task_pane, text="Clif to LADR", \
                command=lambda: ladr(self.selected_file, self.module))
            clif_to_ladr.pack(side=TOP)
            clif_to_tptp = Button(self.task_pane, text="Clif to TPTP", \
                command=lambda: tptp(self.selected_file, self.module))
            clif_to_tptp.pack(side=TOP)
            prove_lemma = Button(self.task_pane, text="Prove Lemma", \
                command=lambda: tptp(self.selected_file, self.module))
            prove_lemma.pack(side=TOP)
        else:
            clif_to_ladr_all = Button(self.task_pane, text="Clif to LADR (ALL)", \
                command=lambda: ladr_all(self.selected_folder))
            clif_to_ladr_all.pack(side=TOP)
            clif_to_tptp_all = Button(self.task_pane, text="Clif to TPTP (ALL)", \
                command=lambda: ladr_all(self.selected_folder))
            clif_to_tptp_all.pack(side=TOP)
            prove_lemma_all = Button(self.task_pane, text="Prove Lemma (ALL)", \
                command=lambda: prove_all(self.selected_folder))
            prove_lemma_all.pack(side=TOP)

        #static buttons
        #view_log = Button(self.task_pane, text="View Log", \
        #        command=lambda: .open_macleod_log())
        #view_log.pack(side=BOTTOM)
        #clear_workspace = Button(self.task_pane, text="Clear Modules", \
        #        command=self.deforestation())
        #clear_workspace.pack(side=BOTTOM)

        self.task_pane.grid(row=0, column=1, stick=E+W+S+N, rowspan=2)
        # going to need to reset this pane, or remove it,
        #then redraw, lets say if user picks a folder,
        # and then decides to choose a file

    def scroll_start(self, event):
        """ Launch internal TKinter mouse track """

        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        """ Adjust the canvas by the amount of mouse pan """

        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def getOption(self, event):
        """ Determine what to do with the selected option """

        if self.default_dropdown_text.get() == "File...":
            self.askopenfilename()
        elif self.default_dropdown_text.get() == "Folder...":
            self.askdirectory()

    def drawReport(self):
        self.report = Report(self.module, self.notebook)
        self.report.build_top()
        self.report.draw_report()
        self.report.create_report_tab()

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
        self.drawReport()

    def askopenfilename(self):
        """ Returns a selected directory name """

        self.selected_file = tkinter.filedialog.askopenfilename()
        self.selected_path.set("  Path:\t"+self.selected_file)
        self.default_dropdown_text.set("Choose Ontology...")
        self.deforestation()
        if self.selected_file is not None:
            self.drawTree(self.selected_file)
            self.create_task_pane("file")

    def askdirectory(self):
        """ Returns a selected directory name """

        self.selected_folder = tkinter.filedialog.askdirectory()
        self.selected_path.set("  Path:\t"+self.selected_folder)
        self.default_dropdown_text.set("Choose Folder...")
        self.deforestation()
        self.create_task_pane("folder")

    def deforestation(self):
        """ Remove the drawn tree after selecting another file/folder to run"""
        #self.arborist.remove_tree()
        self.canvas.delete(ALL)
        for i in range(len(self.notebook.tabs())):
            if i > 1:
                self.notebook.forget(i)

    def set_scroll(self):
        """ set the scroll regions to be the size of the bbox """
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.console_text.config(scrollregion=self.console_text.bbox(ALL))

def main():
    """ Create a new GUI object """
    root = Tk()

    img1 = PhotoImage("img_close", file=os.path.join(img_dir, 'close.gif'))
    img2 = PhotoImage("img_closeactive", file=os.path.join(img_dir, 'close_active.gif'))
    img3 = PhotoImage("img_closepressed", file=os.path.join(img_dir, 'close_pressed.gif'))

    root.bind_class("TNotebook", "<ButtonPress-1>", btn_press, True)
    root.bind_class("TNotebook", "<ButtonRelease-1>", btn_release)

    root.geometry()
    #root.resizable(0, 0)
    app = GUI(root)
    app.load_window()
    root.mainloop()

if __name__ == '__main__':
    main()
