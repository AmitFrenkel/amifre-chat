import emoji
import os
from simpledialog import ask_string
import tkinter.messagebox
import tkinter.filedialog
import time
from Notification import *
from available import *
import varibles


# The following class creates the menu bar of the main chat.
class MenuBar:
    def __init__(self, root, client_name, client_socket, my_cursor, my_database, txt, e1, mem_list, handle_data):
        self.__root = root
        self.__my_cursor = my_cursor
        self.__my_database = my_database
        self.__client_name = client_name
        self.__client_socket = client_socket
        self.__handle_data = handle_data
        self.__txt = txt
        self.__e1 = e1
        self.__mem_list = mem_list
        self.__root.bind('<Control-s>', lambda x: self.save_chat())
        self.__root.bind('<Control-S>', lambda x: self.save_chat())
        self.__root.bind('<Control-o>', lambda x: self.openfile())
        self.__root.bind('<Control-O>', lambda x: self.openfile())
        self.__menu_bar = Menu(self.__root)
        self.__edit = Menu(self.__menu_bar, tearoff=0)
        self.__font = Menu(self.__edit, tearoff=0)
        self.__background = Menu(self.__edit, tearoff=0)
        self.__emoji = Menu(self.__menu_bar, tearoff=0)
        self.__emoji.add_command(label='open emoji', command=em)
        self.menu_bar_building()

    # The following function validating that the user wants to exit.
    def alt_f4(self):
        msg1 = tkinter.messagebox.askquestion('Exit chat', 'Are you sure you want to exit the chat')
        if msg1 == 'yes':   
            self.__root.destroy()
            time.sleep(1.0)

    # The following function builds all the sections of the menu bar.
    def menu_bar_building(self):
        self.file_bar()
        self.edit_bar()
        self.options_bar()
        self.__menu_bar.add_cascade(label="Emoji", menu=self.__emoji)
        self.__root.config(menu=self.__menu_bar)

    # The following function builds the options bar.
    def options_bar(self):
        options = Menu(self.__menu_bar, tearoff=0)
        options.add_command(label="view managers", command=self.view_managers)
        options.add_command(label="view members", command=self.view_members)
        options.add_command(label="logout", command=self.logout)
        options.add_separator()
        options.add_command(label="delete my account", command=self.delete_account)
        self.__menu_bar.add_cascade(label="Options", menu=options)

    # The following function builds the edit bar.
    def edit_bar(self):
        self.txt_bar()
        self.entry_bar()
        self.root_background()
        self.__edit.add_cascade(label="Font", menu=self.__font)
        self.__edit.add_cascade(label="background", menu=self.__background)
        self.__menu_bar.add_cascade(label="Edit", menu=self.__edit)

    # The following function changes the colors of the text.
    def txt_bar(self):
        self.__font.add_command(label="text font color", command=self.txt_font_color)
        self.__background.add_command(label="text background color", command=self.txt_background_color)

    # The following function changes the colors of the text.
    def entry_bar(self):
        self.__font.add_command(label="input font color", command=self.entry_font_color)
        self.__background.add_command(label="input background color", command=self.entry_background_color)

    # The following function creates the command to change the background color of of the window.
    def root_background(self):
        self.__background.add_command(label="background color", command=self.root_background_color)

    # The following function creates the file bar.
    def file_bar(self):
        file = Menu(self.__menu_bar, tearoff=0)
        file.add_command(label="Open", command=self.openfile)
        file.add_command(label="Save", command=self.save_chat)
        file.add_command(label="Print", command=self.to_printer)
        file.add_separator()
        file.add_command(label="Exit", command=lambda: self.alt_f4())
        self.__menu_bar.add_cascade(label="File", menu=file)

    # The following function write to the server that the user wants to get the manager list.
    def view_managers(self):
        self.__client_socket.write((self.__client_name + '0101view-managers').encode())

    # The following function write to the server that the user wants to get the member list.
    def view_members(self):
        self.__client_socket.write((self.__client_name + '0101view-members').encode())

    # The following function delete the user completely from the chat.
    def delete_account(self):
        msg1 = tkinter.messagebox.askquestion('Delete account', 'Are you sure you want to delete your account')
        if msg1 == 'yes':
            self.__my_cursor.execute("DELETE FROM users WHERE name=%s", (self.__client_name[1:],))
            self.__my_cursor.execute("DELETE FROM private_chats WHERE name=%s", (self.__client_name[1:],))
            self.__my_cursor.execute("ALTER TABLE private_chats DROP COLUMN " + self.__client_name[1:])
            self.__my_database.commit()
            self.__root.destroy()

    # The following function saves the chat to an external text/word file.
    def save_chat(self):
        files = [('Text Document', '*.txt'), ('Word Document', '.doc')]
        file = tkinter.filedialog.asksaveasfile(mode='w', filetypes=files, defaultextension=files)
        if file is not None:
            with open(file.name, "w", encoding='utf-8') as document:
                document.write(self.__txt.get(0.0, END))

    # The following function opens to the chat an external text/word file.
    def openfile(self):
        files = [('Text Document', '*.txt'), ('Word Document', '.doc')]
        filename = tkinter.filedialog.askopenfilename(parent=self.__root, filetypes=files, defaultextension=files)
        if filename is not None and filename != '':
            with open(filename, encoding='utf-8', mode='r') as file:
                data = file.read()
                if self.__handle_data.get_mute() == 'True':
                    Notification('You can not speak here').start()
                    return
                self.__txt.config(state=NORMAL)
                try:
                    self.__txt.insert(END, data + '\n')
                except:
                    self.__txt.insert(END, "Your device doesn't support this type of message" + '\n')
                self.__txt.yview(END)
                self.__txt.config(state=DISABLED)
                self.__client_socket.write((self.__client_name+'01'+data).encode())
                self.__my_cursor.execute("SELECT chat FROM users WHERE name=%s ", (self.__client_name[1:],))
                msg = self.__my_cursor.fetchone()
                if msg[0] is not None:
                    my_chat = msg[0]
                    message = my_chat+DATE+' '+str(time.strftime("%H:%M")) + ' '+self.__client_name[1:]+': '+data+'\n'
                    message = emoji.demojize(message)
                    self.__my_cursor.execute("UPDATE users SET chat = %s", (message,))

    # The following function changes the background color of the text.
    def txt_background_color(self):
        try:
            color = ask_string('background color', 'write a color')
            if color == 'available colors':
                Available(self.__root)
                return
            if color == 'default':
                color = 'black'
            self.__txt.configure(background=color)
            self.add_color_db(color, 'text_background_color')
        except:
            Notification("This color doesn't exist").start()

    # The following function changes the background color of the entry.
    def entry_background_color(self):
        try:
            color = ask_string('background color', 'write a color')
            if color == 'available colors':
                Available(self.__root)
                return
            if color == 'default':
                color = 'black'
            self.__e1.configure(background=color)
            self.add_color_db(color, 'input_background_color')

        except:
            Notification("This color doesn't exist").start()

    # The following function changes the background color of the window.
    def root_background_color(self):
        try:
            color = ask_string('background color', 'write a color')
            if color == 'available colors':
                Available(self.__root)
                return
            if color == 'default':
                color = '#025E73'
            self.__root.configure(background=color)
            self.add_color_db(color, 'root_background_color')
        except:
            Notification("This color doesn't exist").start()

    # The following function changes the font color of the text.
    def txt_font_color(self):
        try:
            color = ask_string('font color', 'write a color')
            if color == 'available colors':
                Available(self.__root)
                return
            if color == 'default':
                color = '#FB2412'
            self.__txt.configure(fg=color)
            self.add_color_db(color, 'text_font_color')
        except:
            Notification("This color doesn't exist").start()

    # The following function changes the font color of the entry.
    def entry_font_color(self):
        try:
            color = ask_string('font color', 'write a color')
            if color == 'available colors':
                Available(self.__root)
                return
            if color == 'default':
                color = '#FB2412'
            self.__e1.configure(fg=color, insertbackground=color)
            self.add_color_db(color, 'input_font_color')
        except:
            Notification("This color doesn't exist").start()

    # The following function saves the user preferences in the database.
    def add_color_db(self, color, column):
        self.__my_cursor.execute("UPDATE users SET " + column + "= %s WHERE name = %s", (color, self.__client_name[1:]))
        self.__my_database.commit()

    # The following function disconnects the user from the chat.
    def logout(self):
        msg1 = tkinter.messagebox.askquestion('Logout', 'Are you sure you want to logout?')
        if msg1 == 'yes':
            varibles.logout = True
            self.__root.destroy()

    # The following function prints the chat.
    def to_printer(self):
        msg = tkinter.messagebox.askquestion('print', 'Do you want to print the chat?')
        if msg == 'yes':
            with open("print.txt", "w", encoding='utf-8') as document:
                document.write(self.__txt.get(0.0, END))
            os.startfile("print.txt", "print")
            threading.Timer(30, lambda: delete_file()).start()


# The following function delete the file that the former function created.
def delete_file():
    os.remove("print.txt")


# The following function opens windows virtual keyboard.
def em():
    os.system("wmic process where name='TabTip.exe' delete")
    os.startfile("C:\\Program Files\\Common Files\\microsoft shared\\ink\\TabTip.exe")
