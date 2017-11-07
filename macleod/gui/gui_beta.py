from tkinter import *
import tkinter.scrolledtext as st
from gui_menu import GUIMenu

class Editor(st.ScrolledText):
    def __init__(self, *args, **kwargs):
        st.ScrolledText.__init__(self, *args, **kwargs)

class BebopApp(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        frame = MainView(container, self)
        self.frames[MainView] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainView)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainView(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        textPad = Editor(self, width=100, height=20)
        textPad.pack(side="left")
        var = StringVar()
        sidebar = Label(self, textvariable=var)
        var.set("FUTURE HOME OF INFO BAR")
        sidebar.pack(side="right")

app = BebopApp()
menubar = GUIMenu(app)

app.title("macleod")
app.config(menu=menubar)
app.mainloop()