import threading
import tkinter.messagebox


#  The following class inherit from threading and creates a thread which gives an error message to the user.
class Notification(threading.Thread):
    def __init__(self, data):
        super(Notification, self).__init__()
        self.__data = data
        self.daemon = True

    def run(self):
        tkinter.messagebox.showerror('Error', self.__data)
