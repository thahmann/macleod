"""
@Author Evan Sampson

Extension of Menu for macleod
"""
from tkinter import Menu

class GUIMenu(Menu):
    def __init__(self, *args, **kwargs):
        Menu.__init__(self, *args, **kwargs)
        filemenu = Menu(self, tearoff=0)

        filemenu.add_command(label="Close", command=close)
        self.add_cascade(label="File", menu=filemenu)


def close():
    exit();