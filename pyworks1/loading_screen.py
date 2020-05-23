from tkinter import *
from tkinter import Label
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import time


# This class creates a tkinter window which present a loading window.
class LoadingScreen:
    # The constructor of the class.
    def __init__(self):
        self.__window = self.create_window()
        self.__loading_bar = None
        self.create_logo()
        self.__title = self.create_titles()
        self.__window.config(bg='black')
        self.create_loading_bar()
        self.__window.mainloop()

# The following creates the window, the window's title and icon and prevent the resize option.
    def create_window(self):
        window = Tk()
        window.geometry("300x300+615+180")
        window.title('Amifre Chat')
        window.iconbitmap('icon.ico')
        window.resizable(height=False, width=False)
        return window

# The following function positing the logo in the tkinter window.
    def create_logo(self):
        image_file = Image.open('icon.ico').resize((200, 200))
        img = ImageTk.PhotoImage(image_file)
        image_label = Label(self.__window, bg='black', image=img)
        image_label.pack()
        image_label.image = img

# The following function create the status title of the loading.
    def create_titles(self):
        title = Label(self.__window, text='Getting User Settings...', bg='black', fg='#00FF00',
                      font=('Comic Sans MS', 10))
        title.pack(fill=BOTH)
        return title

# The following function changes the progress bar and the status of the loading
    def create_loading_bar(self):
        # 20% progress
        self.__loading_bar = Progressbar(self.__window, orient=HORIZONTAL,
                                         length=round(self.__window.winfo_screenwidth()/12.8), mode='determinate')
        self.__loading_bar.pack()
        self.__loading_bar['value'] = 20
        self.__window.update_idletasks()
        time.sleep(1.2)
        self.__title.config(text='Retrieving Data...')

        # 50% progress
        self.__loading_bar['value'] = 50
        self.__window.update_idletasks()
        time.sleep(1.2)
        self.__title.config(text='Building Application...')

        # 80% progress
        self.__loading_bar['value'] = 80
        self.__window.update_idletasks()
        time.sleep(1.2)
        self.__title.config(text='Starting Application...')

        # 100% progress
        self.__loading_bar['value'] = 100
        self.__window.update_idletasks()
        time.sleep(1.0)
        self.__window.destroy()
