"""
@Author Robert Powell && Nate Swan

High-level overview of graphical element to be added to Macleod

"""

from Tkinter import *
import ttk

def main():
  
    # Toplevel GUI element
    root = Tk()

    # Use the ttk frames to hold content for compatibility
    content = ttk.Frame(root)
    frame = ttk.Frame(content, borderwidth=5, relief="sunken", height=500, width=500)

    # Labels work like this
    new_label = ttk.Label(content, text="A Label")

    # Entry field work like this
    new_entry = ttk.Entry(content)

    # Variables used in frame work like this
    var_one = BooleanVar() # For checkboxes
    var_one.set(True)
    var_two = StringVar() # For entries

    # Assign those variables to elements in gui
    checkbox_one = ttk.Checkbutton(content, text="First", variable=var_one, onvalue=True)
    ok_button = ttk.Button(content, text="Ok")

    # Grid the variables on the gui like so
    content.grid(column=0, row=0)
    frame.grid(column=0, row=0, columnspan=5, rowspan=5)

    new_label.grid(column=1, row=1)
    new_entry.grid(column=2, row=2)

    checkbox_one.grid(column=3, row=3)
    ok_button.grid(column=4, row=4)

    root.mainloop()


if __name__ == '__main__':
    main()
