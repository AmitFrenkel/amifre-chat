from tkinter import *
import threading
import time
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile, askopenfilename
from color_thread import ColorThreadPrivate
import os
import tkinter.messagebox
from varibles import *
import emoji


# The following class inherit from threading and creates a tkinter window which presents a private chat.
class PrivateChatThread(threading.Thread):
    def __init__(self, sender_name, client_name, message, current_socket, command_number, my_database, my_cursor,
                 color_list):
        super(PrivateChatThread, self).__init__()
        self.daemon = True
        self.__sender_name = sender_name
        self.__client_name = client_name[1:]
        self.__message = message
        self.__current_socket = current_socket
        self.__command_number = command_number
        self.__my_database = my_database
        self.__my_cursor = my_cursor
        self.__entry = None
        self.__txt = None
        self.__window = None
        self.__label = None
        self.__header_label = None
        self.__menu_bar = None
        self.__file_menu = None
        self.__s = None
        self.__my_chat = ''
        self.__options_menu = None
        self.__color = color_list

    # The following function responsible for ongoing functioning of the private chat.
    def run(self):
        self.__txt, self.__window, self.__entry, self.__label, self.__header_label = self.create_private_chat_window()
        self.__window.title('Chatting with: ' + self.__sender_name)
        self.__menu_bar = Menu(self.__window)
        self.__file_menu = Menu(self.__menu_bar, tearoff=0)
        self.__options_menu = Menu(self.__menu_bar, tearoff=0)
        self.create_file_menu()
        self.create_options_menu()
        self.__window.config(menu=self.__menu_bar)
        self.__window.bind('<Control-s>', lambda x: self.save_chat())
        self.__window.bind('<Control-S>', lambda x: self.save_chat())
        self.__window.bind('<Control-o>', lambda x: self.open_file())
        self.__window.bind('<Control-O>', lambda x: self.open_file())
        self.__entry.bind('<Return>', self.get_input_in_private_message)
        if self.__command_number == '6':
            self.update_chat(self.__message)
        self.__window.protocol("WM_DELETE_WINDOW", self.exit_private_chat)
        ColorThreadPrivate(self.__window, self.__txt, self.__entry, self.__client_name).start()
        self.__window.mainloop()

    # The following function creates the window's objects.
    def create_private_chat_window(self):
        window = Tk()
        window.iconbitmap('icon.ico')
        window.geometry(str(round(window.winfo_screenwidth()/3.072)) + "x" +
                        str(round(window.winfo_screenheight()/1.63)))
        window.configure(background=self.get_color('root_background_color'))
        window.resizable(height=False, width=False)
        window.bind('<Control-p>', lambda x: self.to_printer())
        window.bind('<Control-P>', lambda x: self.to_printer())
        window.config(bg=self.get_color('root_background_color'))
        label = Label(window, background=self.get_color('root_background_color'))
        header_label = Label(window)
        header_label.pack(side='top', fill='x')
        label.pack(fill="both", expand=True)
        txt = Text(label, width=150, height=28, wrap=WORD,
                   background=self.get_color('text_background_color'), fg=self.get_color('text_font_color'))
        txt.place(x=0)
        self.__my_cursor.execute('SELECT ' + self.__sender_name + ' FROM private_chats WHERE name=%s',
                                 (self.__client_name,))
        message_from_database = self.__my_cursor.fetchone()
        if message_from_database is not None and message_from_database[0]:
            self.__my_chat = message_from_database[0]
            txt.config(state=NORMAL)
            msg_list = message_from_database[0].split('\n')
            for message in msg_list:
                m = message.split()
                if m:
                    message_tag = 'The message date is ' + m[0] + ' ' + m[1]
                    message = ' '.join(m[1:])
                    message = emoji.emojize(message)
                    txt.insert(END, message + '\n', (message_tag,))
                    txt.tag_bind(message_tag, "<Enter>", lambda event, date=message_tag: self.show_info(date))
                    txt.tag_bind(message_tag, "<Leave>", lambda event, date=message_tag: self.show_info(""))
            txt.yview(END)
            txt.config(state=DISABLED)
        entry = Entry(label, width=200, relief='solid', bd=1, bg=self.get_color('input_background_color'),
                      fg=self.get_color('input_font_color'), insertbackground=self.get_color('input_font_color'))
        self.__s = Scrollbar(label, command=txt.yview, orient=VERTICAL)
        entry.place(x=0, y=462)
        txt.place(x=0)
        txt.configure(yscrollcommand=self.__s.set)
        self.__s.pack(side=RIGHT, fill=BOTH)
        return txt, window, entry, label, header_label

    # The following function updates the chat and the database with every new message that the client receives.
    def update_chat(self, data):
        if data != "" or data is not None:
            sdata = data.split()
            if len(sdata) > 2 or self.__txt.compare("end-1c", "!=", "1.0"):
                self.__txt.config(state=NORMAL)
                message_tag = 'The message date is ' + DATE + ' ' + str(time.strftime("%H:%M"))
                self.__txt.insert(END, data + '\n', (message_tag,))
                self.__txt.tag_bind(message_tag, "<Enter>", lambda event, date=DATE: self.show_info(message_tag))
                self.__txt.tag_bind(message_tag, "<Leave>", lambda event, date=DATE: self.show_info(""))
                self.__txt.yview(END)
                self.__txt.config(state=DISABLED)
            else:
                self.__txt.config(state=NORMAL)
                message_tag = 'The message date is ' + DATE + ' ' + str(time.strftime("%H:%M"))
                self.__txt.insert(END, data + 'Hi I want to start chatting with you' + '\n', (message_tag,))
                self.__txt.tag_bind(message_tag, "<Enter>", lambda event, date=DATE: self.show_info(message_tag))
                self.__txt.tag_bind(message_tag, "<Leave>", lambda event, date=DATE: self.show_info(""))
                self.__txt.yview(END)
                self.__txt.config(state=DISABLED)
            self.save_chat_db(data)

    # The following function shows the data and the time of the text that the cursor is hover.
    def show_info(self, text):
        self.__header_label.configure(text=text)

    # The following function gets the input from the entry widget sending it to server,
    # presenting in the current text widget and updating the database.
    def get_input_in_private_message(self, event):
        text = self.__entry.get()
        text = text.strip()
        self.__txt.config(state=NORMAL)
        if text != "" and text is not None:
            message_tag = 'The message date is ' + DATE + ' ' + str(time.strftime("%H:%M"))
            self.__txt.insert(END, str(time.strftime("%H:%M")) + " " + text + '\n', (message_tag,))
            self.__txt.tag_bind(message_tag, "<Enter>", lambda event1, date=message_tag: self.show_info(date))
            self.__txt.tag_bind(message_tag, "<Leave>", lambda event1, date=message_tag: self.show_info(""))
        self.__txt.yview(END)
        self.__txt.config(state=DISABLED)
        self.__entry.delete(0, 'end')
        self.save_chat_db(str(time.strftime("%H:%M"))+' '+text)
        self.__current_socket.write(self.message_by_client(text).encode())

    # The following function building the message structure according to the protocol before sending it to the server.
    def message_by_client(self, message):
        message = '05' + self.__sender_name + ' ' + message
        return str(len(self.__client_name))+self.__client_name + message

    # The following function prevent from the private chat from being closed is being minimized when the
    # user wants to close it.
    def exit_private_chat(self):
        message_box = messagebox.askquestion('Exit Private Chat?', 'Are you sure you want to exit the private chat?',
                                             icon='warning')
        if message_box == 'yes':
            self.__window.withdraw()

    # The following function gets a specific color from the server.
    def get_color(self, var):
        self.__my_cursor.execute('SELECT ' + var + ' FROM users WHERE name=%s ', (self.__client_name,))
        message_from_database = self.__my_cursor.fetchone()
        if message_from_database is not None:
            return message_from_database[0]

    # The following function creates the file menu.
    def create_file_menu(self):
        self.__file_menu.add_command(label='Clear Chat', command=self.clear_chat)
        self.__file_menu.add_command(label='Open', command=self.open_file)
        self.__file_menu.add_command(label='Save', command=self.save_chat)
        self.__file_menu.add_command(label="Print", command=self.to_printer)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label='Exit', command=self.exit_private_chat)
        self.__menu_bar.add_cascade(label='File', menu=self.__file_menu)

    # The following function creates the options menu.
    def create_options_menu(self):
        self.__options_menu.add_command(label='open emoji', command=em)
        self.__menu_bar.add_cascade(label="Emoji", menu=self.__options_menu)

    # The following function save the chat to an external text or word file.
    def save_chat(self):
        files = [('Text Document', '*.txt'), ('Word Document', '.doc')]
        file = asksaveasfile(mode='w', filetypes=files, defaultextension=files)
        if file is not None:
            with open(file.name, "w", encoding='utf-8') as document:
                document.write(self.__txt.get(0.0, END))

    # The following function open an external text or word file and inserting it to the chat.
    def open_file(self):
        files = [('Text Document', '*.txt'), ('Word Document', '.doc')]
        filename = askopenfilename(parent=self.__window, filetypes=files, defaultextension=files)
        if filename is not None and filename != '':
            with open(filename, encoding='utf-8', mode='r') as file:
                data = file.read()
                self.__txt.config(state=NORMAL)
                self.__txt.insert(END, data + '\n')
                self.__txt.yview(END)
                self.__txt.config(state=DISABLED)
                self.__current_socket.write((self.__client_name + '01' + data).encode())

    # The following function clear the text widget.
    def clear_chat(self):
        self.__txt.config(state=NORMAL)
        self.__txt.delete('1.0', END)
        self.__txt.config(state=DISABLED)

    # The following function save the 'text' parameter to the database.
    def save_chat_db(self, text):
        self.__my_chat = self.__my_chat + DATE + ' ' + emoji.demojize(text) + '\n'
        text2save = (self.__my_chat, self.__client_name)
        sql = "UPDATE private_chats SET " + self.__sender_name + "=%s WHERE name=%s "
        self.__my_cursor.execute(sql, text2save)

    # The following function printing the chat.
    def to_printer(self):
        msg = tkinter.messagebox.askquestion('print', 'Do you want to print the chat?')
        if msg == 'yes':
            with open("print.txt", "w", encoding='utf-8') as document:
                document.write(self.__txt.get(0.0, END))
            os.startfile("print.txt", "print")
            threading.Timer(30, lambda: delete_file()).start()

    # The accessors of the class:
    def get_client_name(self):
        return self.__sender_name

    def get_window(self):
        return self.__window

    def get_chat_data(self):
        return self.__txt.get('1.0', END).strip('\n')

    def get_chat_txt(self):
        return self.__txt


# The following function delete the file that to_printer function created.
def delete_file():
    os.remove("print.txt")


# The following function opens windows virtual keyboard.
def em():
    os.system("wmic process where name='TabTip.exe' delete")
    os.startfile("C:\\Program Files\\Common Files\\microsoft shared\\ink\\TabTip.exe")
