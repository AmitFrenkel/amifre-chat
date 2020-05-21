import threading
from database import Database


#  The following class inherit from threading and checks if the user that the class gets is muted.
class MuteThread(threading.Thread):
    def __init__(self, client_name):
        super(MuteThread, self).__init__()
        self.__client_name = client_name
        self.__d = Database()

    def run(self):
        self.__d.get_my_cursor().execute('SELECT mute FROM users where name=%s ', (self.__client_name[1:],))
        msg = (self.__d.get_my_cursor().fetchone()[0])
        print(msg)
        return msg
