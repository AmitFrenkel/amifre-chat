import socket
import select
import time
import ssl
from varibles import *
import mysql.connector


# The following class creates a server for chat app that bind to the 'HOST' and 'PORT' parameters.
# This server supports multiple connections.
class Server:
    def __init__(self):
        self.__my_database, self.__my_cursor = self.database()
        self.__context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.__context.load_cert_chain(certfile=CERT)
        self.__server_socket = socket.socket()
        self.create_a_server()
        self.__messages_to_send = []
        self.__open_client_sockets = []
        self.__member_list = []
        self.__manager_list = []
        self.__muted_members_list = []
        self.__timer = 0
        self.communication_with_clients()

    # The following function create connection between the database and the server.
    def database(self):
        my_database = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='am1103',
            database='dbchat'
        )
        my_cursor = my_database.cursor()
        return my_database, my_cursor

    # The following function prepares the server for communication with clients.
    def create_a_server(self):
        self.__server_socket.bind((Host, Port))
        self.__server_socket.listen(50)

    # The following function control the communication of the server with the clients.
    def communication_with_clients(self):
        while self.__timer < 150:
            if not self.__open_client_sockets:
                self.__timer += 1
                time.sleep(1)
                print(self.__timer)
            else:
                self.__timer = 0
            rlist, wlist, xlist = select.select([self.__server_socket] + self.__open_client_sockets,
                                                self.__open_client_sockets, [], 0)
            for current_socket in rlist:
                if current_socket is self.__server_socket:
                    (new_socket, address) = self.__server_socket.accept()
                    new_socket = self.__context.wrap_socket(new_socket, server_side=True)
                    self.__open_client_sockets.append(new_socket)
                else:
                    data = (current_socket.recv(1024)).decode()
                    print(data)
                    if data == "":
                        self.__open_client_sockets.remove(current_socket)
                        print("Connection with all the clients closed.")
                        self.__server_socket.close()
                    else:
                        self.__messages_to_send.append((current_socket, self.handle_data(data, current_socket)))
            self.send_waiting_messages(wlist)

    # The following function sends the messages from the clients.
    def send_waiting_messages(self, wlist):
        for message in self.__messages_to_send:
            (client_socket, data) = message
            for client_socket1 in wlist:
                if client_socket1 is not client_socket:
                    client_socket1.write((str(data) + '\n').encode('utf-8'))
            self.__messages_to_send.remove(message)

    # The following function disconnects a client from the server.
    def disconnect_a_client(self, client_socket, client_name):
        self.__open_client_sockets.remove(client_socket)
        self.__member_list.remove((client_socket, client_name))
        self.__messages_to_send.append((client_socket, '3'+client_name))
        if self.is_manager(client_socket, client_socket):
            self.__manager_list.remove((client_socket, client_name))
        client_socket.write('ok'.encode())
        return '6'+client_name + ' left the chat'

    # The following function handles with the data that the server received from the client.
    def handle_data(self, data, current_socket):
        name_len = int(data[0])
        client_name = data[1:name_len + 1]
        client_name1 = client_name
        data1 = data[name_len + 1:]
        command = data1[:2]
        data1 = data1[2:]
        if (current_socket, client_name) not in self.__member_list:
            self.add_member(current_socket, client_name)
        if data1 == '01quit':
            return self.disconnect_a_client(current_socket, client_name1)
        if data1 == '':
            return
        if command == '03':
            if self.is_manager(current_socket, client_name1):
                return self.kick_a_member(data1, client_name1, current_socket)
            else:
                current_socket.write(('1' + 'You are not a manager').encode('utf-8'))
                return ''
        if command == '02':
            return self.command_2(client_name1, current_socket, data1)
        if command == '04':
            if self.is_manager(current_socket, client_name1):
                self.unmute_a_member(data1, client_name1, current_socket)
                return ''
            current_socket.write(('1' + 'You are not a manager').encode('utf-8'))
        if (current_socket, client_name1) in self.__muted_members_list and command != '05':
            current_socket.write(('1' + 'You can not speak here').encode('utf-8'))
            return ''
        if command == '05':
            data2 = data1
            data2 = data2.split()
            data_to_send = ' '.join(data2[1:])
            private_client_name = data2[0]
            self.private_message(private_client_name, data_to_send, current_socket)
            return ''
        if command == '06':
            if self.is_manager(current_socket, client_name1):
                for current_member in self.__member_list:
                    (current_member_socket, current_member_name) = current_member
                    if current_member_name == data1:
                        self.remove_manager_db(current_member_socket, current_member_name)
                        return ''
                current_socket.write(('1' + data1 + ' doesn\'t exist in the chat').encode('utf-8'))
                return ''
            current_socket.write(('1' + 'You are not a manager').encode('utf-8'))
            return ''
        if command == '07':
            if self.is_manager(current_socket, client_name1):
                self.mute_a_member(data1, client_name1, current_socket)
                return ''
            current_socket.write(('1' + 'You are not a manager').encode('utf-8'))
        if (current_socket, client_name1) in self.__muted_members_list and command != '05':
            current_socket.write(('1' + 'You can not speak here').encode('utf-8'))
            return ''
        if data1 == '01view-managers':
            current_socket.write(('6' + self.view_managers()).encode('utf-8'))
            return ''
        if data1 == '01view-members':
            current_socket.write(('6' + self.view_members()).encode('utf-8'))
            return ''
        if command == '01':
            return '1' + str(time.strftime("%H:%M")) + ' ' + client_name + ': ' + data1
        current_socket.write('1You didn\'t enter the right structure of a message'.encode('utf-8'))
        return ''

    def command_2(self, client_name1, current_socket, data1):
        if self.is_manager(current_socket, client_name1):
            for current_member in self.__member_list:
                (current_member_socket, current_member_name) = current_member
                if current_member_name == data1:
                    self.add_manager_db(current_member_socket, current_member_name)
                    return ''
            current_socket.write(('1' + data1 + ' doesn\'t exist in the chat').encode('utf-8'))
            return ''
        current_socket.write(('1' + 'You are not a manager').encode('utf-8'))
        return ''

    # The following function adds a client to the member list.
    def add_member(self, client_socket, name):
        self.__my_cursor.execute("SELECT mute FROM users WHERE name=%s", (name,))
        msg = self.__my_cursor.fetchone()
        if msg is not None:
            if msg[0] == 'True':
                self.__muted_members_list.append((client_socket, name))
        # print(name)
        self.add_manager(client_socket, name)
        self.__member_list.append((client_socket, name))
        self.update_member_list(client_socket)

    # The following function updates the member list.
    def update_member_list(self, client_socket):
        member_to_send = ''
        for i in self.__member_list:
            member = i[1]
            if i in self.__manager_list:
                # print(i[1])
                member = '@' + member
            if i in self.__muted_members_list:
                member = '<muted>' + member
            member_to_send += member + '\n'
        # print('<' + member_to_send + '>')
        client_socket.write(('2' + member_to_send).encode())
        self.__messages_to_send.append((client_socket, '2' + member_to_send))

    # The following function adds a member to the manager list.
    def add_manager(self, client_socket, name):
        self.__my_cursor.execute("SELECT admin FROM users WHERE name=%s", (name,))
        msg = self.__my_cursor.fetchone()
        if msg is not None:
            if msg[0] == 'True':
                self.__manager_list.append((client_socket, name))
                self.__messages_to_send.append((client_socket, name + ' is now a manager'))
                client_socket.write(INFO_TO_A_MANAGER.encode())

    # The following function adds a manager to the database.
    def add_manager_db(self, client_socket, name):
        if (client_socket, name) not in self.__manager_list:
            self.__my_cursor.execute("UPDATE users SET admin='True' WHERE name=%s ", (name,))
            self.__my_database.commit()
            self.add_manager(client_socket, name)
        else:
            client_socket.write('1the command is currently unavailable'.encode())
        self.update_member_list(client_socket)

    # The following function removes a manager to the database.
    def remove_manager_db(self, client_socket, name):
        if (client_socket, name) in self.__manager_list:
            self.__my_cursor.execute("UPDATE users SET admin='False' WHERE name=%s ", (name,))
            self.__my_database.commit()
            self.__manager_list.remove((client_socket, name))
        else:
            client_socket.write('1the command is currently unavailable'.encode())

        self.update_member_list(client_socket)

    # The following function kicks a member.
    def kick_a_member(self, name, the_requesting_client_name, the_requesting_client_socket):
        if name == the_requesting_client_name:
            the_requesting_client_socket.write(('1'+'You can\'t kick your self').encode('utf-8'))
            return ''
        for current_member in self.__member_list:
            (current_member_socket, current_name) = current_member
            if current_name == name:
                self.__member_list.remove(current_member)
                if self.is_manager(current_member_socket, name):
                    self.__manager_list.remove(current_member)
                if current_member_socket in self.__open_client_sockets:
                    current_member_socket.write(('1'+str(time.strftime("%H:%M")) + ' ' + the_requesting_client_name + ' ' +
                                                 'had been kicked you out from the chat').encode())
                    self.__open_client_sockets.remove(current_member_socket)
                    the_requesting_client_socket.write(('1'+str(time.strftime("%H:%M")) + ' ' + 'You kicked' + ' ' + name +
                                                        ' out from the chat!').encode('utf-8'))
                    return '1'+str(time.strftime("%H:%M")) + ' ' + name + ' ' + 'had been kicked from the chat!'
        the_requesting_client_socket.write(('1'+name + ' ' + 'This client does not exist').encode('utf-8'))
        self.update_member_list(the_requesting_client_socket)

    # The following function checks if a target member is a manager.
    def is_manager(self, client_socket, name):
        return (client_socket, name) in self.__manager_list

    # The following function unmute a target client.
    def unmute_a_member(self, name, the_requesting_client_name, the_requesting_client_socket):
        if name == the_requesting_client_name:
            the_requesting_client_socket.write('1You can\'t unmute yourself'.encode('utf-8'))
            return ''
        for current_member in self.__member_list:
            (current_member_socket, current_member_name) = current_member
            # print('4'+current_member_name)
            if current_member_name == name:
                if current_member in self.__muted_members_list:
                    self.__muted_members_list.remove(current_member)
                    the_requesting_client_socket.write(('6You have unmuted ' + name).encode())
                    current_member_socket.write(("6You have been unmuted by "+the_requesting_client_name).encode())
                    self.__my_cursor.execute('UPDATE users SET mute="False" where name=%s ', (name,))
                    self.__my_database.commit()
                    self.update_member_list(the_requesting_client_socket)
                    return ''
        the_requesting_client_socket.write('6the command is currently unavailable'.encode())
        return ''

    # The following function mute a target client.
    def mute_a_member(self,  name, the_requesting_client_name, the_requesting_client_socket):
        # print(name + '>' + the_requesting_client_name)
        if name == the_requesting_client_name:
            the_requesting_client_socket.write('1You can\'t mute yourself'.encode('utf-8'))
            return ''
        for current_member in self.__member_list:
            (current_member_socket, current_member_name) = current_member
            if current_member_name == name:
                if current_member not in self.__muted_members_list:
                    self.__muted_members_list.append(current_member)
                    the_requesting_client_socket.write(('6You have muted ' + name).encode())
                    current_member_socket.write(("6You have been muted by " + the_requesting_client_name).encode())
                    self.__my_cursor.execute('UPDATE users SET mute="True" where name=%s ', (name,))
                    self.__my_database.commit()
                    self.update_member_list(the_requesting_client_socket)
                    return ''
        the_requesting_client_socket.write('6the command is currently unavailable'.encode())
        return ''

    # THe following function sends a private message to a target client.
    def private_message(self, receiver_name, message, sender_socket):
        sender_name = ''
        for current_member1 in self.__member_list:
            (s, sender_name) = current_member1
            if s == sender_socket:
                break
        for current_member in self.__member_list:
            (current_member_socket, current_member_name) = current_member
            if current_member_name == receiver_name:
                if current_member_socket == sender_socket:
                    sender_socket.write(('1'+'You can\'t send a private message to yourself').encode('utf-8'))
                    return ''
                current_member_socket.write(
                    ('4'+str(time.strftime("%H:%M")) + ' ' + sender_name + ': ' + message).encode('utf-8'))
                return ''
        sender_socket.write(('1'+'This client does not exists').encode('utf-8'))
        return ''

    # The following function returns a string that contains all the managers in tha database.
    def view_managers(self):
        s = 'Managers:'
        self.__my_cursor.execute("SELECT name FROM users WHERE admin='True'")
        manager_list_db = self.__my_cursor.fetchall()
        for current_manager in manager_list_db:
            s = s + '\n' + current_manager[0]
        return s

    # The following function returns a string that contains all the members in tha database.
    def view_members(self):
        s = 'Members:'
        self.__my_cursor.execute("SELECT name FROM users ")
        manager_list_db = self.__my_cursor.fetchall()
        for current_manager in manager_list_db:
            s = s + '\n' + current_manager[0]
        return s


if __name__ == '__main__':
    Server()
