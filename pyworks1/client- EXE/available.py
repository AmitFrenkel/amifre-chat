from tkinter import *
from varibles import *


# The following class creates a new tkinter window which contains all the available colors of tkinter.
class Available:
    def __init__(self, root):
        self.__window = Toplevel(root)
        self.__window.geometry("500x520")
        self.__txt = Text(self.__window, width=60, height=30, wrap=WORD, state=DISABLED)
        self.__txt.place(x=0)
        self.__s = Scrollbar(self.__window, command=self.__txt.yview, orient=VERTICAL)
        self.__s.config(command=self.__txt.yview)
        self.__txt.configure(yscrollcommand=self.__s.set)
        self.__s.pack(side=RIGHT, fill=BOTH)
        self.__window.resizable(FALSE, FALSE)
        self.display()

    # The following function insert the available colors.
    def display(self):
        self.__txt.config(state=NORMAL)
        self.__txt.insert(END, '\n')
        self.__txt.yview(END)
        self.__txt.insert(END, '\n')
        self.__txt.yview(END)
        self.__txt.insert(END, COLORS)
        self.__txt.yview(END)
        self.__txt.config(state=DISABLED)
