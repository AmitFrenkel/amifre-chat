from info_thread import Info
from Notification import Notification
from simpledialog import ask_string
import threading
from tkinter import *
import tkinter.font
import tkinter.messagebox
from database import Database
import time
from color_thread import ColorThread


# The following class inherit from threading and build a tkinter window which present a profile page.
class Profile(threading.Thread):
    def __init__(self, root, user, me, client_socket, mem_list, profile_list):
        super(Profile, self).__init__()
        self.__profile_list = profile_list
        self.__d = Database()
        self.__user = user.strip('\n')
        self.__me = me.strip('\n')
        self.__client_socket = client_socket
        self.__mem_list = mem_list
        self.__manager = False
        self.__window = Toplevel(root)
        self.__window.iconbitmap('icon.ico')
        self.__mute_button = Button(self.__window, text="unmute", command=self.mute_member,
                                    bg=self.color('input_background_color'), fg=self.color('input_font_color'), width=22)
        self.__management_button = Button(self.__window, text="Add to the management", command=self.add_manager,
                                          bg=self.color('input_background_color'), fg=self.color('input_font_color'), width=22)
        title = tkinter.font.Font(family='COMIC', size=20, weight=tkinter.font.BOLD)
        self.__title = Label(self.__window, text=self.__user + ' profile\n\n', font=title,
                             fg=self.color('text_font_color'),
                             bg=self.color('text_background_color'))
        self.__private_chat_or_self_button = Button(self.__window, text="Private chat", command=self.private_message,
                                                    bg=self.color('input_background_color'),
                                                    fg=self.color('input_font_color'), width=22)
        self.__l2 = Label(self.__window, text='\n\n', bg=self.color('text_background_color'))
        self.__l3 = Label(self.__window, text='\n\n', bg=self.color('text_background_color'))
        self.__l4 = Label(self.__window, text='\n\n', bg=self.color('text_background_color'))
        self.__kick_button = Button(self.__window, text="kick", command=self.kick_a_member,
                                    bg=self.color('input_background_color'), fg=self.color('input_font_color'), width=22)
        self.__window.protocol("WM_DELETE_WINDOW", lambda: self.alt_f4())

    # The following function responsible for ongoing functioning of the private chat.
    def run(self):
        self.__window.geometry(str(round(self.__window.winfo_screenwidth()/4.8))+'x' +
                               str(round(self.__window.winfo_screenheight()/2.7)))
        self.__window.config(bg=self.color('text_background_color'))
        self.__window.resizable(width=False, height=False)
        self.__title.pack()
        if self.__user != self.__me[1:]:
            self.__private_chat_or_self_button.pack()
            if self.is_manager(self.__me[1:]):
                self.__l2.pack()
                self.__management_button.pack()
                if self.is_manager(self.__user):
                    self.__management_button.config(text="Remove from management")
                else:
                    self.__management_button.config(text="Add to the management")
                self.__l3.pack()
                self.__mute_button.pack()
                if self.is_muted():
                    self.__mute_button.config(text='unmute')
                else:
                    self.__mute_button.config(text='mute')
                self.__l4.pack()
                self.__kick_button.pack()
        else:
            self.__private_chat_or_self_button.config(command=self.change_password, text='change password')
            self.__private_chat_or_self_button.pack()
        ColorThread(self.__window, self.__title, self.__l2, self.__l3, self.__mute_button, self.__management_button, self.__private_chat_or_self_button, self.__kick_button,
                    self.__l4, self.__user).start()

    # The following function building the message structure according to the protocol before sending it to the server.
    def private_message(self):
        self.__client_socket.write((self.__me + '05' + self.__user + '').encode())

    # The following function checks if user is manager
    def is_manager(self, manager):
        self.__d.get_my_cursor().execute("SELECT admin FROM users WHERE name=%s", (manager,))
        msg = self.__d.get_my_cursor().fetchone()
        if msg is not None:
            if msg[0] == 'True':
                self.__manager = True
                return True
        self.__manager = False
        return False

    # The following function changes the manager button.
    def add_manager(self):
        if self.__management_button.cget('text') == "Add to the management":
            self.__client_socket.write((self.__me + '02'+self.__user).encode())
        else:
            self.__client_socket.write((self.__me + '06'+self.__user).encode())

        time.sleep(0.5)
        if self.is_manager(self.__user):
            self.__management_button.config(text="Remove from management")
        else:
            self.__management_button.config(text="Add to the management")

    # The following function checks if member is muted.
    def is_muted(self):
        self.__d.get_my_cursor().execute('SELECT mute FROM users where name=%s ', (self.__user,))
        msg = self.__d.get_my_cursor().fetchone()[0]
        if msg == 'True':
            return True
        return False

    # The following changes the mute button.
    def mute_member(self):
        if self.__mute_button.cget('text') == 'mute':
            self.__client_socket.write((self.__me + '07'+self.__user).encode())
        else:
            self.__client_socket.write((self.__me + '04'+self.__user).encode())
        time.sleep(0.5)
        if self.is_muted():
            self.__mute_button.config(text='unmute')
        else:
            self.__mute_button.config(text='mute')

    # The following function gets a specific color from the server.
    def color(self, color):
        self.__d.get_my_cursor().execute("SELECT " + color + " FROM users WHERE name=%s ", (self.__user,))
        return self.__d.get_my_cursor().fetchone()[0]

    # The following function kick the member.
    def kick_a_member(self):
        self.__client_socket.write((self.__me + '03'+self.__user).encode())

    # The following function changes 'self.__me' password.
    def change_password(self):
        password = ask_string('Password', 'Enter your new password')
        if password is not None:
            password = password.strip()
            if not password or not password.isalnum():
                Notification('invalid password').start()
                return
            self.__d.get_my_cursor().execute('UPDATE users SET password="'+password+'" WHERE name=%s', (self.__me[1:],))
            Info('password has been changed successfully to '+password).start()

    # The accessors:
    def get_window(self):
        return self.__window

    def alt_f4(self):
        self.__window.destroy()
        del self.__profile_list[self.__user]

    def get_manager(self):
        return self.__manager
