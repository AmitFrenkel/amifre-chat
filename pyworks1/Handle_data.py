import random
from info_thread import Info
import threading
import select
from PrivateChat import PrivateChatThread
from Notification import Notification
from tkinter import *
import tkinter.messagebox
import time
from varibles import *


# The following function handles the data that user gets form the server.
class HandleData(threading.Thread):
    def __init__(self, client_socket, mem_list, txt, my_database, my_cursor, root, client_name, private_chat_list,
                 color_list, header_label):
        super(HandleData, self).__init__()
        self.daemon = True
        self.__color = color_list
        self.__header_label = header_label
        self.__private_chat_list = private_chat_list
        self.__client_socket = client_socket
        self.__mem_list = mem_list
        self.__txt = txt
        self.__my_database = my_database
        self.__my_cursor = my_cursor
        self.__root = root
        self.__client_name = client_name
        self.__mute = False

    # The following function checks if there are messages form the server and client can get those messages.
    def run(self):
        while True:
            r, w, x = select.select([self.__client_socket], [], [], 0.00001)
            if self.__client_socket in r:
                data = self.__client_socket.recv(1024).decode()
                print(data)
                if data[0] == '1':
                    print(1)
                    a = self.command_1(data)
                    if a == 0:
                        break
                    # continue
                if data[0] == '2':
                    print(2)
                    self.add_to_mem_list(data)
                    # continue
                if data[0] == '3':
                    print(3)
                    self.remove_from_mem_list(data)
                    # continue
                elif data[0] == '4':
                    print(4)
                    self.command_4(data)
                elif data[0] == '5':
                    print(5)
                    self.command_5(data)
                if data == 'ok':
                    for private_chat in self.__private_chat_list:
                        private_chat.get_window().destroy()
                    break
                if data[0] == '6':
                    Info(data[1:]).start()

    # The following function opens a private chat window.
    def command_5(self, data):
        split_data = data.split()
        sen_name = split_data[1]
        sender_name = sen_name[:len(sen_name) - 1]
        if self.is_private_member(sender_name):
            for private_chat in self.__private_chat_list:
                if sender_name == private_chat.get_client_name():
                    private_chat.get_window().deiconify()
        else:
            private_message_thread = PrivateChatThread(sender_name, self.__client_name, '',
                                                       self.__client_socket, '7', self.__my_database,
                                                       self.__my_cursor, self.__color)
            self.__private_chat_list.append(private_message_thread)
            private_message_thread.start()

    # The following function gets the private messages and adds them to the right private chat.
    def command_4(self, data):
        split_data = data.split()
        sen_name = split_data[1]
        sender_name = sen_name[:len(sen_name) - 1]
        if self.is_private_member(sender_name):
            for private_chat in self.__private_chat_list:
                if sender_name == private_chat.get_client_name():
                    private_chat.get_window().deiconify()
                    private_chat.get_previous_messages(data[1:])
        else:
            private_message_thread = PrivateChatThread(sender_name, self.__client_name, data[1:],
                                                       self.__client_socket, '6', self.__my_database,
                                                       self.__my_cursor, self.__color)
            self.__private_chat_list.append(private_message_thread)
            private_message_thread.start()

    # The following function handles with action that you made or has been made on you or if you get a regular message.
    def command_1(self, data):
        data = data[1:]
        if 'had been kicked you out from the chat' in data:
            self.kick_from_chat(data)
            return 0
        if 'You have unmuted' in data or 'You have muted' in data or 'You have been muted by' in data \
                or 'You have been unmuted by' in data:
            Info(data).start()
            return 1
        if 'You can\'t kick your self' in data or 'You are not a manager' in data \
                or ' doesn\'t exist in the chat' \
                in data or 'This client does not exist' in data or \
                'You can\'t mute yourself' in data or 'is not in the chat' in data or \
                ' doesn\'t exist in the chat' in data \
                or "You can't send a private message to yourself" in data:
            Notification(data).start()
            return 1
        else:
            self.regular_msg(data)
            return 1

    # The following function removes a specific member name form the member list in the chat app.
    def remove_from_mem_list(self, data):
        ind = self.__mem_list.get(0, END).index(data[1:])
        self.__mem_list.delete(ind)

    # The following function adds a specific member name form the member list in the chat app.
    def add_to_mem_list(self, data):
        self.__mem_list.delete(0, END)
        list_data = data[1:].split()
        print('<2>'+data)
        for i in list_data:
            if i[0] == '@':
                i = i[1:]
                self.__mem_list.insert(END, i + '\n')
                self.__mem_list.yview(END)
                self.__mem_list.itemconfig(self.__mem_list.size() - 1, foreground="yellow")
            elif i[0] == '<':
                i = i.replace('<muted>', '')
                i = i.replace('@', '')
                self.__mem_list.insert(END, i + '\n')
                self.__mem_list.yview(END)
                self.__mem_list.itemconfig(self.__mem_list.size() - 1, foreground="orange")
            else:
                self.__mem_list.insert(END, i + '\n')
                self.__mem_list.yview(END)

    # The following function displays a regular message in the main chat.
    def regular_msg(self, data):
        split_data = data.split()
        sen_name = split_data[1]
        sender_name = sen_name[:len(sen_name) - 1]
        if data != "" or data is not None:
            self.__txt.config(state=NORMAL)
            if sender_name not in self.__color:
                self.__color[sender_name] = random.choice(COLORS)
            self.__txt.highlight_pattern(sen_name, self.__color[sender_name])
            message_tag = 'The message date is ' + DATE + ' ' + str(time.strftime("%H:%M"))
            self.__txt.insert(END, data + '\n', (message_tag,))
            self.__txt.tag_bind(message_tag, "<Enter>", lambda event, date=DATE: self.show_info(message_tag))
            self.__txt.tag_bind(message_tag, "<Leave>", lambda event, date=DATE: self.show_info(""))
            self.__txt.highlight_pattern(sen_name, self.__color[sender_name])
            self.__txt.yview(END)
            self.__txt.config(state=DISABLED)

    # The following function shows the information about message that cursor is hover.
    def show_info(self, text):
        self.__header_label.configure(text=text)

    # The following function kicks a member from the chat.
    def kick_from_chat(self, data):
        tkinter.messagebox.showerror('Error', data)
        self.logout()
        self.__root.destroy()
        # time.sleep(1)
        sys.exit(0)

    # The following function update the database that this specific user logged out from the chat.
    def logout(self):
        sql = "UPDATE users SET connected='False' WHERE name=%s "
        self.__my_cursor.execute(sql, (self.__client_name[1:],))
        self.__my_database.commit()
        self.__client_socket.close()

    # The following function returns if a specific user is muted or not.
    def get_mute(self):
        self.__my_cursor.execute('SELECT mute FROM users where name=%s ', (self.__client_name[1:],))
        msg = (self.__my_cursor.fetchone()[0])
        return msg

    # The following function returns if there is an existing tkinter window of private chat with 'sender_name'.
    def is_private_member(self, sender_name):
        for private_chat in self.__private_chat_list:
            if sender_name == private_chat.get_client_name():
                return True
        return False
