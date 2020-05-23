import threading
import os
from database import Database
from profile import Profile
from tkinter import *
import socket
import ssl
import tkinter.filedialog
import tkinter.messagebox
import tkinter.font
import time
from menu_bar import MenuBar
from Notification import Notification
from Handle_data import HandleData
import emoji
from custom_text import CustomText
import random
from varibles import *
import varibles


# The following class creates the main chat of the app.
class Chat:
    def __init__(self, client_name, window, start):
        self.__profile_list = {}
        self.__private_chat_list = []
        self.__d = Database(varibles.Host)
        self.__color = {}
        self.__my_database = self.__d.get_my_database()
        self.__my_cursor = self.__d.get_my_cursor()
        self.__client_name = client_name
        self.__context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.__client_socket = self.create_connection(varibles.Host, varibles.Port)
        window.destroy()
        start.destroy()
        self.__message_tag = ''
        self.__my_chat = ''
        self.__root = Tk()
        self.__label = Label(self.__root)
        self.__header_label = Label(self.__root)
        self.__header_label.pack(side="top", fill="x")
        self.__label.pack(fill="both", expand=True)
        self.__txt = CustomText(self.__label, wrap=WORD, background=self.color('text_background_color'),
                                fg=self.color('text_font_color'))
        self.__mem_list = Listbox(self.__label, selectmode=SINGLE,
                                  bg=self.color('member_background_color'), fg=self.color('member_font_color'))
        self.__entry = Entry(self.__label, bg=self.color('input_background_color'),
                             fg=self.color('input_font_color'), insertbackground=self.color('input_font_color'))
        self.__handle_data = HandleData(self.__client_socket, self.__mem_list, self.__txt, self.__my_database,
                                        self.__my_cursor, self.__root, self.__client_name, self.__private_chat_list,
                                        self.__color, self.__header_label)
        self.gui()
        self.__root.mainloop()
        self.__client_socket.write((self.__client_name + '0101quit').encode())
        time.sleep(1.0)
        self.exit()

    # The following function creates a secured connection with the server.
    def create_connection(self, host, port):
        client_socket = socket.create_connection((host, port))
        client_socket = self.__context.wrap_socket(client_socket, server_hostname='192.168.1.17')
        return client_socket

    # The following function destroy the window.
    def alt_f4(self):
        msg1 = tkinter.messagebox.askquestion('Exit chat', 'Are you sure you want to exit the chat')
        if msg1 == 'yes':
            self.__root.destroy()
            time.sleep(1.0)

    # The following function gets a specific color from the server.
    def color(self, color):
        self.__my_cursor.execute("SELECT " + color + " FROM users WHERE name=%s ", (self.__client_name[1:],))
        return self.__my_cursor.fetchone()[0]

    # The following function creates the tkinter window objects.
    def gui(self):
        self.__client_socket.write(self.__client_name.encode())
        self.__root.iconbitmap('icon.ico')
        self.__root.title('Amifre chat-client: ' + self.__client_name[1:])
        self.__label.configure(background=self.color('root_background_color'))
        self.__root.geometry(str(round(self.__root.winfo_screenwidth() / 1.28)) + "x" +
                             str(round(self.__root.winfo_screenheight() / 1.66)))
        self.__mem_list.place(relwidth=0.1, relheight=0.95, relx=0)
        self.__mem_list.bind('<Double-1>', lambda x: self.profile_page(self.__mem_list.get(ACTIVE)))
        self.get_previous_messages()
        self.__txt.config(state=DISABLED)
        self.__entry.place(relwidth=1.0, relx=0, rely=0.96)
        self.__txt.place(relwidth=0.88, relheight=0.95, relx=0.1)
        scroll = Scrollbar(self.__label, command=self.__txt.yview, orient=VERTICAL)
        self.__txt.configure(yscrollcommand=scroll.set)
        scroll.pack(side=RIGHT, fill=BOTH)
        self.__entry.bind('<Return>', self.get_input)
        self.__root.bind('<Control-p>', lambda x: self.to_printer())
        self.__root.bind('<Control-P>', lambda x: self.to_printer())
        MenuBar(self.__root, self.__client_name, self.__client_socket, self.__my_cursor, self.__my_database,
                self.__txt, self.__entry, self.__mem_list, self.__handle_data)
        self.__handle_data.start()
        self.__root.minsize(width=round(self.__root.winfo_screenwidth() / 1.85),
                            height=round(self.__root.winfo_screenheight() / 1.75))
        self.__root.protocol("WM_DELETE_WINDOW", self.alt_f4)

    # The following function insert to the text widget all the previous messages.
    def get_previous_messages(self):
        msg_list = self.create_previous_message_list()
        for message in msg_list:
            try:
                if message[2] == '-':
                    m = message.split()
                    self.__message_tag = 'The message date is ' + m[0] + ' ' + m[1]
                    message = ' '.join(m[1:])
                    message = emoji.emojize(message)
                    lmessage = message.split(' ')
                    lmessage = lmessage[1]
                    if lmessage[:-1] == self.__client_name[1:]:
                        index = message.index(lmessage)
                        message = message[:index] + message[index + len(lmessage):]
                        message = message[:5] + message[6:]
                    if lmessage[:-1] not in self.__color:
                        self.__color[lmessage[:-1]] = random.choice(COLORS)
                    self.__txt.tag_configure(self.__color[lmessage[:-1]], foreground=self.__color[lmessage[:-1]])
                    self.__txt.highlight_pattern(lmessage, self.__color[lmessage[:-1]])
                    try:
                        self.__txt.insert(END, message + '\n', (self.__message_tag,))
                        self.__txt.tag_bind(self.__message_tag, "<Enter>",
                                            lambda event, date=self.__message_tag: self.show_info(date))
                        self.__txt.tag_bind(self.__message_tag, "<Leave>",
                                            lambda event, date=self.__message_tag: self.show_info(""))
                        self.__txt.highlight_pattern(lmessage, self.__color[lmessage[:-1]])
                    except:
                        self.__txt.insert(END, "Your device doesn't support this type of message" + '\n')
                else:
                    try:
                        self.__txt.insert(END, message + '\n', (self.__message_tag,))
                        self.__txt.tag_bind(self.__message_tag, "<Enter>",
                                            lambda event, date=self.__message_tag: self.show_info(date))
                        self.__txt.tag_bind(self.__message_tag, "<Leave>",
                                            lambda event, date=self.__message_tag: self.show_info(""))
                    except:
                        self.__txt.insert(END, "Your device doesn't support this type of message" + '\n')
            except:
                pass

    # The following function creates a list of all previous messages.
    def create_previous_message_list(self):
        msg_list = ''
        self.__my_cursor.execute("SELECT chat FROM users")
        msg = self.__my_cursor.fetchall()
        for i in msg:
            if i[0] is not None:
                self.__my_chat = i[0]
                msg_list = i[0].split('\n')
                break
        return msg_list

    # The following function shows the data and the time of the text that the cursor is hover.
    def show_info(self, text):
        self.__header_label.configure(text=text)

    # The following function gets the input from the entry widget sending it to server,
    # presenting in the current text widget and updating the database.
    def get_input(self, event1):
        if self.__handle_data.get_mute() == 'True':
            Notification('You can not speak here').start()
            self.__entry.delete(0, 'end')
            return
        else:
            message = self.__entry.get()
            message = message.strip()
            if message == '' or message is None:
                return ''
            self.__txt.config(state=NORMAL)
            self.__message_tag = 'The message date is ' + DATE + ' ' + str(time.strftime("%H:%M"))
            self.__txt.insert(END, str(time.strftime("%H:%M")) + " " + message + '\n', (self.__message_tag,))
            self.__txt.tag_bind(self.__message_tag, "<Enter>",
                                lambda event, date=self.__message_tag: self.show_info(date))
            self.__txt.tag_bind(self.__message_tag, "<Leave>",
                                lambda event, date=self.__message_tag: self.show_info(""))
            self.__txt.yview(END)
            self.__entry.delete(0, 'end')
            self.__my_chat = self.__my_chat + DATE + ' ' + str(time.strftime("%H:%M")) + " " + self.__client_name[1:]\
                            + ': ' + emoji.demojize(message) + '\n'
            sql = "UPDATE users SET chat = %s "
            self.__my_cursor.execute(sql, (self.__my_chat,))
            message = '01' + message
            self.__client_socket.write((self.__client_name + message).encode())
            self.__txt.config(state=DISABLED)
            if message == '0101quit':
                self.__root.quit()
                self.exit()

    # The following function creates a new profile page if it doesn't exist, and if it does is moving it to the top.
    def profile_page(self, profile):
        profile = profile.strip('\n')
        if profile not in self.__profile_list:
            self.__profile_list[profile] = Profile(self.__root, profile, self.__client_name, self.__client_socket,
                                                   self.__mem_list, self.__profile_list)
            self.__profile_list[profile].start()
        else:
            self.__profile_list[profile].get_window().deiconify()

    # The following function updating the database that the user exit from the chat.
    def exit(self):
        sql = "UPDATE users SET connected='False' WHERE name=%s "
        self.__my_cursor.execute(sql, (self.__client_name[1:],))
        self.__my_database.commit()

    # The following function printing the chat.
    def to_printer(self):
        msg = tkinter.messagebox.askquestion('print', 'Do you want to print the chat?')
        if msg == 'yes':
            with open("print.txt", "w", encoding='utf-8') as document:
                document.write(self.__txt.get(0.0, END))
                document.write(self.__txt.get(0.0, END))
            os.startfile("print.txt", "print")
            threading.Timer(30, lambda: delete_file()).start()


# The following function delete the file that the previous function created
def delete_file():
    os.remove("print.txt")
