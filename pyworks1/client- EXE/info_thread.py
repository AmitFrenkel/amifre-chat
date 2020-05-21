import threading
import tkinter.messagebox


#  The following class inherit from the threading creates and info windows for the user.
class Info(threading.Thread):
    def __init__(self, data):
        super(Info, self).__init__()
        self.__data = data

    def run(self):
        tkinter.messagebox.showinfo('info', self.__data)
