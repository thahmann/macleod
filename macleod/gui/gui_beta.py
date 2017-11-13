from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from os import path
import tkinter.scrolledtext as st

class GUI(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.tab_controller = ttk.Notebook(self)
        tab = Editor(self.tab_controller, self, "")
        self.tab_controller.add(tab, text="NewFile", compound=TOP)
        self.tab_controller.pack()
    def open_file(self, file):
        self.tab_controller.add(Editor(self.tab_controller, self, file.read()),
                                sticky="nsew",
                                text=path.basename(file.name))
    def close(self):
        tab_number = self.tab_controller.index(self.tab_controller.select())
        self.tab_controller

class Editor(Frame):
    def __init__(self, parent, controller, text):
        Frame.__init__(self, parent)
        self.textPad = st.ScrolledText(self)
        self.textPad.pack(fill="both")
        self.textPad.insert(INSERT, text)

class Sidebar(Frame):
    def __init__(self, parent, controller):
        print("STUFF GOES HERE")

app = GUI()

#functions for the menu
def close():
    exit()

def open():
    file = filedialog.askopenfile(filetypes=[("Common Logic Files", "*.clif"),
                                      ("All", '*')],)
    app.open_file(file)


menubar = Menu(app)
filemenu = Menu(menubar, tearoff=0)

filemenu.add_command(label="Open", command = open)
filemenu.add_command(label="Close", command=close)

menubar.add_cascade(label="File", menu=filemenu)

app.title("macleod")
app.config(menu=menubar)
app.mainloop()
