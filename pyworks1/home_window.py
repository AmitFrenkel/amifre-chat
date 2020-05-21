from tkinter import *
from sign_in import Login
from signup import Signup


# The following class create a tkinter window that allow the user to sign in or sign up.
class HomeWindow:
    # THe constructor function of the class.
    def __init__(self, my_database, my_cursor):
        self.__my_database = my_database
        self.__my_cursor = my_cursor
        self.__start = Tk()
        self.__start.iconbitmap('icon.ico')
        self.__start.geometry('+'+str(round(self.__start.winfo_screenwidth()/2.25)) + "+" +
                              str(round(self.__start.winfo_screenheight()/2.98)))
        Button(self.__start, text='Click to login the chat',
               command=lambda: Login(self.__start, self.__my_database, self.__my_cursor), cursor='hand2').grid(row=0)
        Button(self.__start, text='Click to signup the chat',
               command=lambda: Signup(self.__start, self.__my_database, self.__my_cursor), cursor='hand2').grid(row=1)
        self.__start.resizable(False, False)
        self.__client_name = ''
        self.__start.mainloop()

