import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import tkinter.scrolledtext as st
from CustomNotebook import *

FILE_IMAGE = """R0lGODlhEAAQAKEAACEhIa3Y5sDv/yEhISH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAMALAAAAAAQ
                ABAAAAIy3ICpxiABYwCTnSchrcZljQEdlini9ZVjKp0eq60w98Iuyd4zjaf6fBMIh0TB6WBKGgoAOw=="""
FOLDER_IMAGE = """R0lGODlhEAAQAKEAACEhIa3Y5sDv/yEhISH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAMALAAAAAA
                QABAAAAIrnG+gC8krgpQqTvrg3bfy731bKE5kGZylKrIgYKEpLGMxWgn6zu9NBmwUAAA7"""

class GUI(tk.Tk):
    def __init__(self, project_path, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # set up the window
        self.tab_controller = CustomNotebook(self)
        self.explorer_bar = ExplorerBar(self, project_path)
        self.information_bar = InformationBar(self)
        self.new_tab()

        self.explorer_bar.pack(side="left", fill="y", expand=False, anchor="w")
        self.information_bar.pack(side="right", fill="y", expand=False, anchor="e")
        self.tab_controller.pack(fill="both", expand=True)

    def open_file(self, file):
        new_editor = Editor(self.tab_controller, self, file.read())
        self.tab_controller.add(new_editor, sticky="nsew", text=os.path.basename(file.name))
        self.tab_controller.select(new_editor)

    def save_file(self, file):
        window = self.tab_controller.select()
        current_editor = self.tab_controller.children[window.split('.')[2]]
        buffer = current_editor.textPad.get("1.0", tk.END)
        file.write(buffer)
        self.tab_controller.tab(window, text=os.path.basename(file.name))

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

#https://stackoverflow.com/questions/16746387/tkinter-treeview-widget
class ExplorerBar(ttk.Treeview):
    def __init__(self, parent, project_path):
        ttk.Treeview.__init__(self, parent)
        self.file_img = PhotoImage(data=FILE_IMAGE)
        self.folder_img = PhotoImage(data=FOLDER_IMAGE)
        root_node = self.insert('', 'end', text=os.path.abspath(project_path), open=True)
        self.generate_directory(root_node, project_path)

    def generate_directory(self, parent, path):
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            isdir = os.path.isdir(abspath)
            cur_image = self.file_img if not isdir else self.folder_img
            oid = self.insert(parent, 'end', text=p, open=False, image=cur_image)
            if isdir:
                self.generate_directory(oid, abspath)
app = GUI(os.curdir)


def open():
    file = filedialog.askopenfile(filetypes=[("Common Logic Files", "*.clif"),
                                      ("All", '*')],)
    app.open_file(file)

def save():
    activewindow = app.tab_controller.select()
    filename = app.tab_controller.tab(activewindow, option="text")
    file = filedialog.asksaveasfile(initialfile=filename, mode='w', defaultextension=".clif", filetypes=[("Common Logic Files", "*.clif"),
                                      ("All", '*')], initialdir=os.curdir)
    app.save_file(file)

def new():
    app.new_tab()

menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)

filemenu.add_command(label="New File", command=new)
filemenu.add_command(label="Open", command=open)
filemenu.add_command(label="Save", command=save)
filemenu.add_command(label="Quit", command=exit)

menubar.add_cascade(label="File", menu=filemenu)

app.title("macleod")
app.config(menu=menubar)
app.mainloop()
