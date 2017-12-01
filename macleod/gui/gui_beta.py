import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from os import path
import tkinter.scrolledtext as st
from CustomNotebook import *

class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # set up the window
        self.tab_controller = CustomNotebook(self)
        self.explorer_bar = ExplorerBar(self)
        self.information_bar = InformationBar(self)
        self.new_tab()

        self.explorer_bar.pack(side="left", fill="y", expand=True, anchor="w")
        self.information_bar.pack(side="right", fill="y", expand=True, anchor="e")
        self.tab_controller.pack(fill="both", expand=True)

    def open_file(self, file):
        new_editor = Editor(self.tab_controller, self, file.read())
        self.tab_controller.add(new_editor, sticky="nsew", text=path.basename(file.name))
        self.tab_controller.select(new_editor)

    def save_file(self, file):
        window = self.tab_controller.select()
        current_editor = self.tab_controller.children[window.split('.')[2]]
        buffer = current_editor.textPad.get("1.0", tk.END)
        file.write(buffer)
        self.tab_controller.tab(window, text=path.basename(file.name))

    def new_tab(self):
        tab = Editor(self.tab_controller, self, "")
        self.tab_controller.add(tab, sticky="nsew")
        self.tab_controller.tab(tab, text="Untitled "+str(self.tab_controller.index("end"))+".clif")
        self.tab_controller.select(tab)

class Editor(tk.Frame):
    def __init__(self, parent, controller, text):
        tk.Frame.__init__(self, parent)
        self.textPad = st.ScrolledText(self)
        self.textPad.pack(fill="both", expand=True)
        self.textPad.insert(tk.INSERT, text)

class InformationBar(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent)

class ExplorerBar(ttk.Treeview):
    def __init__(self, parent):
        ttk.Treeview.__init__(self, parent)

app = GUI()

#functions for the menu
def quit():
    exit()

def open():
    file = filedialog.askopenfile(filetypes=[("Common Logic Files", "*.clif"),
                                      ("All", '*')],)
    app.open_file(file)

def save():
    activewindow = app.tab_controller.select()
    filename = app.tab_controller.tab(activewindow, option="text")
    file = filedialog.asksaveasfile(initialfile=filename, mode='w', defaultextension=".clif", filetypes=[("Common Logic Files", "*.clif"),
                                      ("All", '*')],)
    app.save_file(file)

def new():
    app.new_tab()

menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)

filemenu.add_command(label="New File", command=new)
filemenu.add_command(label="Open", command=open)
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Quit", command=quit)

menubar.add_cascade(label="File", menu=filemenu)

app.title("macleod")
app.config(menu=menubar)
app.mainloop()
